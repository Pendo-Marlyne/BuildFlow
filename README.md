# 🏗 Chartered Investment Dashboard 

## 📖 Overview
The **Chartered Investment Dashboard** is a Python + Tkinter application connected to MongoDB Atlas. It simulates how a construction company manages stock, investments and distribution. The system provides a professional interface for tracking materials, purchases, warehouse stock and BuilderDistributors transfers while also offering user authentication with role‑based access.

---

## ✨ Features
- **Authentication System**
  - User registration and login with roles (Admin, Manager, Auditor).
  - Corporate‑style access control.

- **Dashboard**
  - Portfolio summary with account balance.
  - Material inventory table.
  - Transaction highlights.
  - Purchase workflow with balance updates.

- **Reports**
  - Summaries of total spend, usage and profit/loss.
  - Cashbook entries for income and expenses.

- **Profile Page**
  - User details (name, email, role).
  - Edit or delete account.
  - Purchase history and cashbook summary.

- **Warehouse Management**
  - Add, edit, and delete warehouse stock.
  - Record incoming stock to update availability.

- **BuilderDistributors Management**
  - Add, edit, and delete distributor products.
  - Corporate distributor view for outgoing stock.

- **Transfers**
  - Move stock from warehouse to BuilderDistributors.
  - Delete unwanted transfer records.

---

## 🛠 Tech Stack
- **Python** (core logic)
- **Tkinter** (GUI interface)
- **MongoDB Atlas** (cloud database)
- **python‑dotenv** (secure environment variable management)

---

## 🚀 Setup & Usage
1. Clone the repository.
2. Create a `.env` file in the project root with your MongoDB URI:
