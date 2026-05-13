def determine_stage(days_overdue):

    if 1 <= days_overdue <= 7:
        return "Stage 1 - Warm & Friendly"

    elif 8 <= days_overdue <= 14:
        return "Stage 2 - Polite but Firm"

    elif 15 <= days_overdue <= 21:
        return "Stage 3 - Formal & Serious"

    elif 22 <= days_overdue <= 30:
        return "Stage 4 - Stern & Urgent"

    elif days_overdue > 30:
        return "ESCALATE TO FINANCE TEAM"

    else:
        return "Not Overdue"