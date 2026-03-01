import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

from constants import CATEGORIES
from db.expenses import get_expenses, add_expense, delete_expense

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
    left, right = st.columns([1, 2])

    # ── Add Expense Form ──
    with left:
        st.subheader("➕ Add Expense")
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

        # ── Budget Thresholds ──
        st.subheader("🎯 Monthly Budgets")
        st.caption("Set a monthly limit per category to track overspending.")

        if "budgets" not in st.session_state:
            st.session_state.budgets = {}

        with st.form("budget_form", clear_on_submit=False):
            for cat in CATEGORIES:
                current = st.session_state.budgets.get(cat, 0)
                val = st.number_input(
                    cat, min_value=0.0, value=float(current),
                    step=50.0, format="%.0f", key=f"budget_{cat}"
                )
                st.session_state.budgets[cat] = val
            st.form_submit_button("Save Budgets", use_container_width=True)

    # ── Right column ──
    with right:
        # Stacked monthly bar chart
        if not df.empty:
            st.subheader("📊 Monthly Spending")

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
                xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=12, color="#4a4a6a")),
                yaxis=dict(showgrid=False, zeroline=False, tickprefix="$", tickfont=dict(size=11, color="#9090a8"), showline=False),
                margin=dict(t=10, b=100, l=10, r=10),
                height=380,
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="DM Sans", bordercolor="#e0e0ee"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── Budget vs Actual ──
        budgets = {k: v for k, v in st.session_state.get("budgets", {}).items() if v > 0}
        if budgets and not df.empty:
            st.subheader("🎯 Budget vs Actual")

            all_months = sorted(df["month_key"].unique(), reverse=True)[:6]
            for month_key in all_months:
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
                    label = f"**+{diff_pct:.0f}% over**" if over else f"{diff_pct:.0f}% under"

                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                        f'<span style="width:100px;font-size:0.82rem;color:#4a4a6a">{cat}</span>'
                        f'<div style="flex:1;background:#f0f0f8;border-radius:20px;height:10px;overflow:hidden">'
                        f'<div style="width:{min(pct,100):.0f}%;background:{bar_color};height:100%;border-radius:20px;transition:width 0.3s"></div>'
                        f'</div>'
                        f'<span style="width:110px;font-size:0.8rem;color:{"#ef4444" if over else "#22c55e"};text-align:right">'
                        f'${actual:,.0f} / ${budget:,.0f} &nbsp; {label}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("---")

        # ── Expense List ──
        st.subheader("📋 Expenses")
        if df.empty:
            st.info("No expenses yet. Add your first one! 👈")
        else:
            # Month filter for list only
            months = df[["month_key", "month_label"]].drop_duplicates().sort_values("month_key", ascending=False)
            month_options = {"All Time": None} | dict(zip(months["month_label"], months["month_key"]))
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                selected_month_label = st.selectbox("Month", list(month_options.keys()), label_visibility="collapsed")
                selected_month = month_options[selected_month_label]
                month_df = df if selected_month is None else df[df["month_key"] == selected_month]
            with fcol2:
                all_cats = ["All Categories"] + sorted(month_df["category"].unique().tolist())
                filter_cat = st.selectbox("Category", all_cats, label_visibility="collapsed")
            with fcol3:
                all_tags = set()
                for t in month_df["tags"].dropna():
                    if isinstance(t, list):
                        all_tags.update(t)
                all_tags = ["All Tags"] + sorted(all_tags)
                filter_tag = st.selectbox("Tag", all_tags, label_visibility="collapsed")

            filtered = month_df.copy()
            if filter_cat != "All Categories":
                filtered = filtered[filtered["category"] == filter_cat]
            if filter_tag != "All Tags":
                filtered = filtered[filtered["tags"].apply(
                    lambda t: filter_tag in t if isinstance(t, list) else False
                )]

            for _, row in filtered.iterrows():
                col_a, col_b, col_c, col_d = st.columns([1.5, 3, 1.5, 0.5])
                with col_a:
                    st.markdown(f"**${row['amount']:,.2f}**")
                with col_b:
                    color = CATEGORY_COLORS.get(row["category"], "#94a3b8")
                    st.markdown(f'<span style="background:{color}22;color:{color};padding:2px 8px;border-radius:6px;font-size:0.8rem">{row["category"]}</span> {row.get("note", "") or ""}', unsafe_allow_html=True)
                    tags = row.get("tags", [])
                    if tags:
                        tag_html = " ".join([f'<span class="tag-badge">#{t}</span>' for t in tags])
                        st.markdown(tag_html, unsafe_allow_html=True)
                with col_c:
                    st.markdown(f"<small style='color:#6b6b80'>{row['date'].strftime('%b %d, %Y')}</small>", unsafe_allow_html=True)
                with col_d:
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        delete_expense(access_token, row["id"])
                        st.rerun()
                st.divider()