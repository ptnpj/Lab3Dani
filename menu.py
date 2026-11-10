import sys
from pymongo import MongoClient
import json

# Підключення до локального екземпляра MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hospital_db"]
collection = db["inpatient_charges"]


def step1_count():
    print("\n    Загальна кількість документів    ")
    pipeline = [
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$out": "result_step1"}
    ]
    collection.aggregate(pipeline)
    res = list(db["result_step1"].find({}, {"_id": 0}))
    if res:
        print(f"Кількість документів у колекції: {res[0].get('count')}")
    else:
        print("Колекція порожня.")


def step2_avg_total():
    print("\n         Середнє значення Average_Covered_Charges для всієї колекції       ")
    pipeline = [
        {"$group": {"_id": None, "avg_covered_charges": {"$avg": "$Average_Covered_Charges"}}},
        {"$out": "result_step2"}
    ]
    collection.aggregate(pipeline)
    res = list(db["result_step2"].find({}, {"_id": 0}))
    if res:
        avg_val = res[0].get("avg_covered_charges")
        print(f"Середнє значення: {avg_val:.2f}")
    else:
        print("Дані відсутні.")


def step3_avg_by_zip():
    print("\n     Середнє значення за кожним поштовим індексом     ")
    pipeline = [
        {
            "$group": {
                "_id": "$Provider_Zip_Code",
                "avg_covered_charges": {"$avg": "$Average_Covered_Charges"}
            }
        },
        {"$sort": {"avg_covered_charges": 1}},
        {"$out": "result_step3"}
    ]
    collection.aggregate(pipeline)
    print(f"{'ZIP-код':<15} | {'Середні витрати ($)':<20}")
    print("-" * 38)
    for doc in db["result_step3"].find().limit(10):
        print(f"{str(doc['_id']):<15} | {doc['avg_covered_charges']:<20.2f}")
    print("... (показано перші 10 записів, результат збережено у result_step3)")


def step4_filtered_zip():
    print("\n     Середнє за ZIP-кодом, де показник менше експериментального    ")
    threshold_input = input("Введіть експериментальний поріг: ").strip()
    threshold = float(threshold_input) if threshold_input else 30000.0

    pipeline = [
        {
            "$group": {
                "_id": "$Provider_Zip_Code",
                "avg_covered_charges": {"$avg": "$Average_Covered_Charges"}
            }
        },
        {"$match": {"avg_covered_charges": {"$lt": threshold}}},
        {"$sort": {"avg_covered_charges": 1}},
        {"$out": "result_step4"}
    ]
    collection.aggregate(pipeline)
    print(f"\nZIP-коди із середнім чеком менше за {threshold}:")
    print(f"{'ZIP-код':<15} | {'Середні витрати ($)':<20}")
    print("-" * 38)
    count = 0
    for doc in db["result_step4"].find().limit(10):
        print(f"{str(doc['_id']):<15} | {doc['avg_covered_charges']:<20.2f}")
        count += 1
    if count == 0:
        print("Записів за таким порогом не знайдено.")
    else:
        print("... (показано перші 10 записів, результат збережено у result_step4)")


def step5_where_and_having():
    print("\n     Фільтрація документів та агрегація    ")
    threshold_input = input("Введіть експериментальний поріг середнього чеку: ").strip()
    threshold = float(threshold_input) if threshold_input else 30000.0

    pipeline = [
        {"$match": {"Average_Medicare_Payments": {"$lt": 50000}}},
        {
            "$group": {
                "_id": "$Provider_Zip_Code",
                "avg_covered_charges": {"$avg": "$Average_Covered_Charges"}
            }
        },
        {"$match": {"avg_covered_charges": {"$lt": threshold}}},
        {"$sort": {"avg_covered_charges": 1}},
        {"$out": "result_step5"}
    ]
    collection.aggregate(pipeline)
    print(f"\nРезультат (Medicare < 50000 і середній чек < {threshold}):")
    print(f"{'ZIP-код':<15} | {'Середні витрати ($)':<20}")
    print("-" * 38)
    count = 0
    for doc in db["result_step5"].find().limit(10):
        print(f"{str(doc['_id']):<15} | {doc['avg_covered_charges']:<20.2f}")
        count += 1
    if count == 0:
        print("Записів за вказаними критеріями не знайдено.")
    else:
        print("... (показано перші 10 записів, результат збережено у result_step5)")


def main_menu():
    while True:
        print("          Меню           ")
        print("1. Кількість документів у колекції")
        print("2. Середнє значення Average_Covered_Charges для всіх")
        print("3. Середнє значення за ZIP-кодом з сортуванням")
        print("4. Середнє за ZIP-кодом менше за поріг")
        print("5. Medicare < 50000 + середнє менше за поріг")
        print("0. Вихід з програми")

        choice = input("Оберіть пункт меню (0-5): ").strip()

        if choice == "1":
            step1_count()
        elif choice == "2":
            step2_avg_total()
        elif choice == "3":
            step3_avg_by_zip()
        elif choice == "4":
            step4_filtered_zip()
        elif choice == "5":
            step5_where_and_having()
        elif choice == "0":
            print("Роботу завершено.")
            sys.exit(0)
        else:
            print("Некоректний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main_menu()