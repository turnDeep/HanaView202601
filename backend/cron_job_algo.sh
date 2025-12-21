#!/bin/bash

# Algoスキャンを実行するCronジョブ

set -e

echo "=========================================="
echo "Algo Scanner Starting: $(date)"
echo "=========================================="

# Pythonパスを設定
export PYTHONPATH=/app:$PYTHONPATH

# Algoスキャンを実行
python -c "
import asyncio
from backend.algo_scanner import run_algo_scan
# backend.main has logic but for cron we can import _send_notifications_to_permission_level if we can access it or reimplement
# data_fetcher.py has the push notification logic but main.py uses it too.
# Let's check backend/algo_scanner.py if it sends notification.
# Yes, run_algo_scan in algo_scanner.py doesn't seem to send notifications itself?
# Wait, algo_scanner.py spec shows it sends notifications?
# Let's check my implemented algo_scanner.py.
# My implementation of algo_scanner.py does NOT send notifications inside run_scan.
# The spec said: 6. ura権限ユーザーにPush通知を送信 -> cron script or api endpoint should handle it.
# The spec's cron_job_algo.sh example imports send_push_notifications_to_permission.
# Let's see if I can import it from backend.main (async function) or backend.data_fetcher.
# backend.data_fetcher.MarketDataFetcher has send_push_notifications but that's instance method.
# backend.main has _send_notifications_to_permission_level.
# It is better to use the logic from main.py if possible, but importing from main might be circular or require app context?
# Actually, the Spec says: use _send_notifications_to_permission_level('ura', ...)
# I should probably add a helper in data_fetcher or security_manager or standalone script.
# Or I can just replicate the logic here or make main.py functions reusable.
# Let's see backend/data_fetcher.py again. It has send_push_notifications.
# But it filters by permission inside.
# I will use a simple script that calls run_algo_scan and then logic for notification.

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Run scan
        result = await run_algo_scan()

        # Send notifications
        # Since we are running outside of FastAPI app context, we can't reuse main.py's function easily if it depends on app state.
        # But we can reuse the logic.

        from backend.data_fetcher import MarketDataFetcher
        fetcher = MarketDataFetcher()

        # Create custom notification data
        total_signals = result['total_scanned']
        notification_data = {
            'title': 'Algoスキャン完了',
            'body': f'新規シグナル: {total_signals}件',
            'type': 'hwb-scan' # Using hwb-scan type to trigger ura/secret filter in fetcher.send_push_notifications
            # Wait, 'type': 'hwb-scan' filters for secret/ura in data_fetcher.py.
            # Spec says Algo is only for 'ura'.
            # I should make sure data_fetcher handles 'algo-scan' or similar if I want specific filtering.
            # Or I can manually send it here.
        }

        # Let's look at data_fetcher.py send_push_notifications logic.
        # if type == 'hwb-scan', it sends to secret and ura.
        # Algo tab is ura only.
        # So I shouldn't use 'hwb-scan'.

        # I will implement notification logic here directly or import security manager.
        from backend.security_manager import security_manager
        from pywebpush import webpush, WebPushException
        import json
        import os

        DATA_DIR = '/app/data'
        security_manager.data_dir = DATA_DIR
        security_manager.initialize()

        subscriptions_file = os.path.join(DATA_DIR, 'push_subscriptions.json')
        if os.path.exists(subscriptions_file):
            with open(subscriptions_file, 'r') as f:
                subscriptions = json.load(f)

            sent_count = 0
            for sub_id, sub_data in subscriptions.items():
                if sub_data.get('permission') == 'ura':
                    try:
                        webpush(
                            subscription_info=sub_data,
                            data=json.dumps(notification_data),
                            vapid_private_key=security_manager.vapid_private_key,
                            vapid_claims={'sub': security_manager.vapid_subject}
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(f'Failed to send to {sub_id}: {e}')

            logger.info(f'Algo notifications sent: {sent_count}')

        print(f'✅ Algo scan completed: {total_signals} signals')

    except Exception as e:
        print(f'❌ Algo scan failed: {e}')
        raise

asyncio.run(main())
"

echo "=========================================="
echo "Algo Scanner Finished: $(date)"
echo "=========================================="
