# Лабораторна робота №1: Основи функціонального програмування у Python

**Варіант №11**: Мобільний тариф  
**Мета**: Реалізувати чисте функціональне ядро для обчислення місячної вартості послуг мобільного зв'язку без побічних ефектів, глобального стану та мутацій даних.

---

## Особливості реалізації

1. **Чисте ядро (`core.py`)**:
   - Містить чисті функції: `calculate_extra_minutes_cost`, `calculate_extra_sms_cost`, `calculate_extra_gb_cost`, `with_monthly_cost`, `compose`.
   - Жодних `print` або глобальних змінних.
   - Створюються нові словники (`ProcessedUsageRecord`) з додаванням розрахованих полів (`monthly_cost`, `extra_*`).
2. **Параметризація та Callable**:
   - `make_tariff_processor` — функція вищого порядку (фабрика), яка приймає фільтри та політики знижок (`typing.Callable`).
   - `make_loyalty_bonus_policy` — фабрика для формування політики лояльності.
3. **Ізоляція I/O (`app.py`)**:
   - Друк звіту винесено у функцію `render_report()`.

---

## Інструкція із запуску

### 1. Налаштування середовища та встановлення залежностей

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt