#!/usr/bin/env python3
"""
Generate Lab 1 synthetic data (customers, products, orders) as CSV files.

Creates assets/lab1/data/{customers,products,orders}.csv for use with
uv run lab1_datagen --local (no ShadowTraffic or Docker required).

Usage:
    uv run generate_lab1_data
    uv run generate_lab1_data --dry-run
    uv run generate_lab1_data --output-dir /tmp/lab1-data
"""

import argparse
import csv
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_SEED = 42

_FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emily", "Frank", "Grace", "Henry",
    "Isabel", "James", "Karen", "Liam", "Maria", "Noah", "Olivia", "Patrick",
    "Quinn", "Rachel", "Samuel", "Taylor", "Uma", "Victor", "Wendy", "Xavier",
    "Yolanda", "Zoe", "Aaron", "Brianna", "Carlos", "Diana",
]

_LAST_NAMES = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Foster", "Garcia",
    "Harris", "Ingram", "Jackson", "Kumar", "Lee", "Martinez", "Nelson",
    "OBrien", "Patel", "Rivera", "Robinson", "Smith", "Taylor",
    "Underwood", "Vargas", "Williams", "Xu", "Young", "Zhang", "Okafor",
    "Nguyen", "Campbell", "Brooks",
]

_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]

_STATES = (
    ["California"] * 3 +
    ["New York"] * 2 +
    ["Texas"] * 2 +
    ["Florida"] +
    ["Washington", "Colorado", "Illinois", "Georgia", "Ohio"]
)

_PRODUCTS = [
    {"product_id": "3001", "product_name": "Apple AirPods Pro 2, Wireless Earbuds, Active Noise Cancellation, Hearing Aid Feature", "price": 245.00, "department": "electronics & technology"},
    {"product_id": "3002", "product_name": "Apple AirTag - 1 Pack, Item Tracker with Apple Find My", "price": 30.00, "department": "electronics & technology"},
    {"product_id": "3003", "product_name": "Bose QuietComfort Headphones, Bluetooth Over Ear Noise Cancelling Headphones, Black", "price": 365.00, "department": "electronics & technology"},
    {"product_id": "3004", "product_name": "Official Hasbro Games Jenga Game with Digital Die, Wood Block Party Game, Family Games, 6+", "price": 28.00, "department": "toys & games"},
    {"product_id": "3005", "product_name": "Coca-Cola Classic Soda Pop, 12 fl oz Cans, 24 Pack", "price": 15.00, "department": "food & beverages"},
    {"product_id": "3006", "product_name": "Dawn EZ-Squeeze Ultra Dish Soap Dishwashing Liquid, Original Scent, 22.0 fl oz", "price": 5.00, "department": "household cleaning & home goods"},
    {"product_id": "3007", "product_name": "JBL Flip 7 - Portable waterproof and drop-proof speaker, Bold JBL Pro Sound with AI Sound Boost, 16Hrs of Playtime, and PushLock system with interchangeable accessories (Black)", "price": 165.00, "department": "electronics & technology"},
    {"product_id": "3008", "product_name": "Monopoly Board Game, Classic Game with Storage Tray and Larger Tokens, Family Games, 8+", "price": 20.00, "department": "toys & games"},
    {"product_id": "3009", "product_name": "Panasonic Eneloop BK-4MCCA4BA Pre-Charged Nickel Metal Hydride AAA Rechargeable Batteries, 4-Battery Pack", "price": 17.00, "department": "electronics & technology"},
    {"product_id": "3010", "product_name": "Scrabble Classic Crossword Board Game for Kids and Family Ages 8 and Up, 2-4 Players", "price": 30.00, "department": "toys & games"},
    {"product_id": "3011", "product_name": "UNO Card Game for Kids, Adults & Family Game Night, Original UNO Game of Matching Colors & Numbers", "price": 10.00, "department": "toys & games"},
    {"product_id": "3012", "product_name": 'Wilson Evolution Official Game Basketball - 29.5"', "price": 100.00, "department": "sports & recreation"},
    {"product_id": "3013", "product_name": "Magic 8 Ball Kids Toy, Novelty Fortune Teller Gag Gift, Ask a Question & Turn Over for Answer", "price": 15.00, "department": "toys & games"},
    {"product_id": "3014", "product_name": "Pyrex 1-cup Measuring Cup", "price": 15.00, "department": "household cleaning & home goods"},
    {"product_id": "3015", "product_name": "Penn Championship Extra Duty Tennis Balls (1 Can, 3 balls)", "price": 8.99, "department": "sports & recreation"},
    {"product_id": "3016", "product_name": "The Grand Budapest Hotel (Blu-ray), 20th Century Fox, Comedy", "price": 16.00, "department": "movies & entertainment"},
    {"product_id": "3017", "product_name": "The Wild Robot (Blu-ray + Digital Copy), Family, DreamWorks", "price": 23.99, "department": "movies & entertainment"},
]


def _iso(epoch_ms: int) -> str:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _generate_customers(rng: random.Random, now_ms: int) -> list:
    updated_at = _iso(now_ms)
    pairs = [(f, l) for f in _FIRST_NAMES for l in _LAST_NAMES]
    rng.shuffle(pairs)
    customers = []
    for i in range(50):
        first, last = pairs[i]
        email = f"{first.lower()}.{last.lower()}@{rng.choice(_EMAIL_DOMAINS)}"
        customers.append({
            "customer_id": f"C-{100000 + i}",
            "customer_email": email,
            "customer_name": f"{first} {last}",
            "state": rng.choice(_STATES),
            "updated_at": updated_at,
        })
    return customers


def _generate_products(now_ms: int) -> list:
    updated_at = _iso(now_ms)
    return [{**p, "updated_at": updated_at} for p in _PRODUCTS]


def _generate_orders(rng: random.Random, customers: list, now_ms: int) -> list:
    selected_products = rng.sample(_PRODUCTS, 10)
    selected_customers = rng.sample(customers, 10)

    # 10 orders × 30s intervals; order 9 (last) lands 5 minutes before now
    base_ms = now_ms - (5 * 60 * 1000)
    orders = []
    for i, (product, customer) in enumerate(zip(selected_products, selected_customers)):
        order_ts_ms = base_ms + (i - 9) * 30_000
        orders.append({
            "order_id": f"O-{(order_ts_ms // 10000) % 1_000_000:06d}",
            "customer_id": customer["customer_id"],
            "product_id": product["product_id"],
            "price": product["price"],
            "order_ts": _iso(order_ts_ms),
        })
    return orders


def _write_csv(path: Path, rows: list, fieldnames: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Lab 1 synthetic CSV data (customers, products, orders)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: assets/lab1/data/)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print counts without writing files")
    args = parser.parse_args()

    from .common.terraform import get_project_root
    project_root = get_project_root()
    output_dir = args.output_dir or (project_root / "assets" / "lab1" / "data")

    rng = random.Random(_SEED)
    now_ms = int(time.time() * 1000)

    customers = _generate_customers(rng, now_ms)
    products = _generate_products(now_ms)
    orders = _generate_orders(rng, customers, now_ms)

    if args.dry_run:
        print(f"customers: {len(customers)}")
        print(f"products:  {len(products)}")
        print(f"orders:    {len(orders)}")
        print("[DRY RUN — no files written]")
        return 0

    _write_csv(output_dir / "customers.csv", customers,
               ["customer_id", "customer_email", "customer_name", "state", "updated_at"])
    _write_csv(output_dir / "products.csv", products,
               ["product_id", "product_name", "price", "department", "updated_at"])
    _write_csv(output_dir / "orders.csv", orders,
               ["order_id", "customer_id", "product_id", "price", "order_ts"])

    print(f"Written to {output_dir}:")
    print(f"  customers.csv  {len(customers)} rows")
    print(f"  products.csv   {len(products)} rows")
    print(f"  orders.csv     {len(orders)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
