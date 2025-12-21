
import sys
import os
import json
import logging
import asyncio

# Add project root to sys.path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    logger.info("Testing imports...")
    try:
        from backend.algo_data_manager import AlgoDataManager
        from backend.algo_scanner import AlgoScanner
        from backend.gemini_client import GeminiClient
        from backend.market_algo_x.ibd_screeners import IBDScreeners
        from backend.stage_algo.gamma_plotter import GammaPlotter
        logger.info("✅ All imports successful.")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_data_manager():
    logger.info("Testing AlgoDataManager...")
    try:
        from backend.algo_data_manager import AlgoDataManager
        manager = AlgoDataManager(data_dir='test_data')

        # Test Save Summary
        summary_data = {"test": "summary", "scan_date": "2025-01-01"}
        if not manager.save_daily_summary(summary_data):
            logger.error("❌ Failed to save summary.")
            return False

        # Test Load Summary
        loaded_summary = manager.load_latest_summary()
        if loaded_summary != summary_data:
            logger.error(f"❌ Loaded summary mismatch: {loaded_summary}")
            return False

        # Test Save Symbol
        symbol_data = {"symbol": "TEST", "data": 123}
        if not manager.save_symbol_data("TEST", symbol_data):
            logger.error("❌ Failed to save symbol data.")
            return False

        # Test Load Symbol
        loaded_symbol = manager.load_symbol_data("TEST")
        if loaded_symbol != symbol_data:
            logger.error(f"❌ Loaded symbol mismatch: {loaded_symbol}")
            return False

        logger.info("✅ AlgoDataManager tests passed.")
        return True
    except Exception as e:
        logger.error(f"❌ AlgoDataManager test exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_scanner_instantiation():
    logger.info("Testing AlgoScanner Instantiation...")
    try:
        from backend.algo_scanner import AlgoScanner
        scanner = AlgoScanner()
        # Mocking or checking internal state if possible, but just instantiation is good first step.
        logger.info("✅ AlgoScanner instantiated.")
        return True
    except Exception as e:
        logger.error(f"❌ AlgoScanner instantiation failed: {e}")
        return False

async def main():
    if not test_imports(): exit(1)
    if not test_data_manager(): exit(1)
    if not await test_scanner_instantiation(): exit(1)

    logger.info("🎉 All Backend Verifications Passed!")

if __name__ == "__main__":
    asyncio.run(main())
