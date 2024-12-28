import asyncio
import IssuerCodeExtractor
import DatabaseManager
import DataScraper


async def main():
    try:

        first_pipe = IssuerCodeExtractor.IssuerCodeExtractor()
        second_pipe = DatabaseManager.DatabaseManager()
        third_pipe = DataScraper.DataScraper(second_pipe)

        thread_number = 200

        print("Getting issuer codes...")
        issuer_codes = first_pipe.get_issuer_codes_from_dropdown()
        print(f"Found {len(issuer_codes)} valid issuer codes\n")

        print("Filtering issuer codes...")
        issuer_codes = first_pipe.filter_codes(issuer_codes)
        print(f"Remaining codes: {len(issuer_codes)}\n")

        print("Checking data currency...")
        update_info = second_pipe.check_data_currency(issuer_codes)
        print(f"{len(update_info)} issuers need updating\n")

        if update_info:
            print("Starting data update...\n")
            await third_pipe.update_data(update_info=update_info)
            print("\nData update completed\n")
        else:
            print("All data is up to date")

        # For debugging purposes
        # print(MSEStockScraper.no_table_codes)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
