import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

from constants import CATEGORIES
from db.expenses import get_expenses, add_expense, delete_expense
from db.misc import get_misc, set_misc

CATEGORY_COLORS = {
    "Food":           "#f97316",
    "Utilities":      "#3b82f6",
    "Health":         "#22c55e",
    "Subscriptions":  "#a855f7",
    "Rent":           "#ef4444",
    "Walmart":        "#0ea5e9",
    "Transport":      "#eab308",
    "Travel":         "#14b8a6",
    "Entertainment":  "#ec4899",
    "Shopping":       "#f43f5e",
    "Other":          "#94a3b8",
}

def show(access_token: str, user_id: str):
    expenses = get_expenses(access_token, user_id)
    df = pd.DataFrame(expenses) if expenses else pd.DataFrame()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df["month_key"] = df["date"].dt.strftime("%Y-%m")
        df["month_label"] = df["date"].dt.strftime("%B %Y")

    # Load budgets from DB
    if "budgets" not in st.session_state or not st.session_state.budgets:
        st.session_state.budgets = get_misc(access_token, user_id, "budgets")

    # ── Metrics ──
    this_month = (
        df[df["month_key"] == date.today().strftime("%Y-%m")]["amount"].sum()
        if not df.empty else 0
    )
    total_budget = sum(v for v in st.session_state.get("budgets", {}).values() if v > 0)
    diff = this_month - total_budget

    col1, col2 = st.columns(2)
    with col1:
        if total_budget > 0:
            arrow = "↑" if diff > 0 else "↓"
            color = "#ef4444" if diff > 0 else "#22c55e"
            label = f"+${diff:,.2f} over" if diff > 0 else f"${abs(diff):,.2f} under"
            html = (
                "<div style='background:#fff;border:1px solid #e0e0ee;border-radius:12px;padding:16px'>"
                "<p style='color:#9090a8;font-size:0.8rem;margin:0 0 4px'>📅 This Month vs Budget</p>"
                f"<p style='color:#1a1a2e;font-size:1.6rem;font-weight:700;margin:0'>${this_month:,.2f}</p>"
                f"<p style='color:{color};font-size:0.85rem;margin:4px 0 0'>{arrow} {label}</p>"
                "</div>"
            )
            st.html(html)
        else:
            st.metric("📅 Total This Month", f"${this_month:,.2f}")
    with col2:
        st.metric("🎯 Monthly Budget", f"${total_budget:,.2f}" if total_budget > 0 else "Not set")

    st.markdown("---")

    # ── Tabs for mobile-friendly navigation ──
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add", "📊 Chart", "🎯 Budgets", "📋 Expenses"])

    # ── Tab 1: Add Expense ──
    with tab1:
        with st.form("add_expense_form", clear_on_submit=True):
            expense_date = st.date_input("Date", value=date.today())
            amount = st.number_input("Amount ($)", min_value=0.0, step=10.0, format="%.2f")
            category = st.selectbox("Category", CATEGORIES)
            note = st.text_input("Note", placeholder="e.g. Lunch at office")
            tags_input = st.text_input("Tags", placeholder="e.g. groceries, weekly")
            submitted = st.form_submit_button("Add Expense", use_container_width=True)

            if submitted:
                if amount > 0:
                    tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
                    success = add_expense(access_token, user_id, expense_date, amount, category, note, False, tags)
                    if success:
                        st.success("Expense added!")
                        st.rerun()
                else:
                    st.warning("Please enter a valid amount.")

    # ── Tab 2: Chart ──
    with tab2:
        if df.empty:
            st.info("No expenses yet.")
        else:
            all_months = sorted(df["month_key"].unique(), reverse=True)[:6]
            chart_df = df[df["month_key"].isin(all_months)].copy()
            chart_df["month_label"] = chart_df["date"].dt.strftime("%b %Y")

            pivot = chart_df.groupby(["month_label", "month_key", "category"])["amount"].sum().reset_index()
            months_ordered = pivot.drop_duplicates("month_key").sort_values("month_key")["month_label"].tolist()
            all_cats = sorted(pivot["category"].unique())

            fig = go.Figure()
            for cat in all_cats:
                cat_data = pivot[pivot["category"] == cat]
                amounts = []
                for m in months_ordered:
                    row = cat_data[cat_data["month_label"] == m]
                    amounts.append(float(row["amount"].values[0]) if len(row) > 0 else 0)

                color = CATEGORY_COLORS.get(cat, "#94a3b8")
                fig.add_trace(go.Bar(
                    name=cat,
                    x=months_ordered,
                    y=amounts,
                    marker=dict(color=color, line=dict(width=0)),
                    hovertemplate=f"<b>{cat}</b><br>$%{{y:,.0f}}<extra></extra>",
                ))

            fig.update_layout(
                barmode="stack",
                barcornerradius=8,
                bargap=0.35,
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="top", y=-0.15,
                    xanchor="center", x=0.5,
                    font=dict(size=11, color="#4a4a6a"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#4a4a6a"),
                xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#4a4a6a")),
                yaxis=dict(showgrid=False, zeroline=False, tickprefix="$", tickfont=dict(size=10, color="#9090a8"), showline=False),
                margin=dict(t=10, b=120, l=0, r=0),
                height=380,
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="DM Sans", bordercolor="#e0e0ee"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Budget vs Actual
            budgets = {k: v for k, v in st.session_state.get("budgets", {}).items() if v > 0}
            if budgets:
                st.markdown("---")
                st.subheader("🎯 Budget vs Actual")
                all_months_ba = sorted(df["month_key"].unique(), reverse=True)[:6]
                for month_key in all_months_ba:
                    month_label = df[df["month_key"] == month_key]["month_label"].iloc[0]
                    month_data = df[df["month_key"] == month_key]
                    cat_totals = month_data.groupby("category")["amount"].sum().to_dict()

                    has_data = any(cat in cat_totals for cat in budgets)
                    if not has_data:
                        continue

                    st.markdown(f"**{month_label}**")
                    for cat, budget in budgets.items():
                        actual = cat_totals.get(cat, 0)
                        if actual == 0:
                            continue
                        pct = (actual / budget) * 100
                        over = pct > 100
                        color = CATEGORY_COLORS.get(cat, "#94a3b8")
                        bar_color = "#ef4444" if over else color
                        diff_pct = pct - 100 if over else 100 - pct
                        label = f"+{diff_pct:.0f}% over" if over else f"{diff_pct:.0f}% under"
                        label_color = "#ef4444" if over else "#22c55e"

                        st.markdown(
                            f'<div style="margin-bottom:10px">'
                            f'<div style="display:flex;justify-content:space-between;margin-bottom:3px">'
                            f'<span style="font-size:0.82rem;color:#4a4a6a">{cat}</span>'
                            f'<span style="font-size:0.78rem;color:{label_color}">${actual:,.0f} / ${budget:,.0f} · {label}</span>'
                            f'</div>'
                            f'<div style="background:#f0f0f8;border-radius:20px;height:8px;overflow:hidden">'
                            f'<div style="width:{min(pct,100):.0f}%;background:{bar_color};height:100%;border-radius:20px"></div>'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                    st.markdown("---")

    # ── Tab 3: Budgets ──
    with tab3:
        st.caption("Set a monthly limit per category.")
        with st.form("budget_form", clear_on_submit=False):
            new_budgets = {}
            for cat in CATEGORIES:
                current = st.session_state.budgets.get(cat, 0)
                val = st.number_input(
                    cat, min_value=0.0, value=float(current),
                    step=50.0, format="%.0f", key=f"budget_{cat}"
                )
                new_budgets[cat] = val
            if st.form_submit_button("Save Budgets", use_container_width=True):
                if set_misc(access_token, user_id, "budgets", new_budgets):
                    st.session_state.budgets = new_budgets
                    st.success("Budgets saved!")

    # ── Tab 4: Expenses ──
    with tab4:
        if df.empty:
            st.info("No expenses yet. Add your first one!")
        else:
            months = df[["month_key", "month_label"]].drop_duplicates().sort_values("month_key", ascending=False)
            month_options = {"All Time": None} | dict(zip(months["month_label"], months["month_key"]))

            col_a, col_b = st.columns(2)
            with col_a:
                selected_month_label = st.selectbox("Month", list(month_options.keys()), label_visibility="collapsed")
                selected_month = month_options[selected_month_label]
                month_df = df if selected_month is None else df[df["month_key"] == selected_month]
            with col_b:
                all_cats = ["All Categories"] + sorted(month_df["category"].unique().tolist())
                filter_cat = st.selectbox("Category", all_cats, label_visibility="collapsed")

            filtered = month_df.copy()
            if filter_cat != "All Categories":
                filtered = filtered[filtered["category"] == filter_cat]

            for _, row in filtered.iterrows():
                color = CATEGORY_COLORS.get(row["category"], "#94a3b8")
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(
                        f'<div style="padding:8px 0">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center">'
                        f'<span style="font-weight:700;font-size:1rem">${row["amount"]:,.2f}</span>'
                        f'<span style="font-size:0.75rem;color:#9090a8">{row["date"].strftime("%b %d")}</span>'
                        f'</div>'
                        f'<div style="margin-top:3px">'
                        f'<span style="background:{color}22;color:{color};padding:1px 8px;border-radius:6px;font-size:0.75rem">{row["category"]}</span>'
                        f'<span style="color:#4a4a6a;font-size:0.85rem;margin-left:6px">{row.get("note", "") or ""}</span>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        delete_expense(access_token, row["id"])
                        st.rerun()
                st.divider()