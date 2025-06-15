from Services.service import Service

def main():
    print("Demo program for CSV file operations")
    curr_file_path = "CSV/fruitSalesData.csv"
    
    try:
        util = Service(curr_file_path)
    except FileNotFoundError as e:
        print(e)
        return

    while True:
        print("\n========= MENU =========")
        print("1. Display rows")
        print("2. Filter rows")
        print("3. Sort rows")
        print("4. Aggregate column")
        print("5. Count valid palindromes")
        print("6. Exit")
        print("========================")
        choice = input("Choose a service (1-6): ").strip()

        if choice == "1":
            try:
                n = int(input("Enter the number of rows to display: ").strip())
                util.display_first_n_rows(n)
            except ValueError:
                print("Invalid number.")

        elif choice == "2":
            col = input("Enter column to filter on: ").strip()
            filter_condition = input("Enter condition (e.g., '> 10','< 10','== 10','!= 10' 'contains Apple'): ").strip()
            nfile_path = input("Enter output CSV path to save result (or press Enter to skip): ").strip()
            util.filter_rows_based_on_condition(col, filter_condition, nfile_path if nfile_path else None)

        elif choice == "3":
            col = input("Enter column to sort by: ").strip()
            sort_order = input("Sort ascending? (yes/no): ").strip().lower()
            ascen_var = sort_order in ['yes', 'y', 'true', '1']
            nfile_path = input("Enter output CSV path to save result (or press Enter to skip): ").strip()
            util.sort_rows_by_column(col, path_for_file=nfile_path if nfile_path else None, ascending=ascen_var)

        elif choice == "4":
            col = input("Enter column for aggregation: ").strip()
            op = input("Operation (sum / average / min / max): ").strip()
            result = util.aggregate_column_data(col, op)
            if result is not None:
                print(f"Result of {op.upper()} on '{col}': {result}")

        elif choice == "5":
            util.check_valid_palindromes()

        elif choice == "6":
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
