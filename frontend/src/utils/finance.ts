import { Transaction } from "../types/Transaction";

export enum PeriodType {
  Monthly = "monthly",
  Quarterly = "quarterly",
  Yearly = "yearly",
}

export interface AggregatedData {
  period: string;
  income: number;
  expense: number;
  balance: number;
}

export const aggregateByPeriod = (
  transactions: Transaction[],
  periodType: PeriodType
): AggregatedData[] => {
  const grouped: Record<string, AggregatedData> = {};

  for (const tx of transactions) {
    const date = new Date(tx.date);
    let periodKey = "";

    switch (periodType) {
      case PeriodType.Monthly:
        periodKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, "0")}`;
        break;
      case PeriodType.Quarterly:
        const quarter = Math.floor(date.getMonth() / 3) + 1;
        periodKey = `${date.getFullYear()}-Q${quarter}`;
        break;
      case PeriodType.Yearly:
        periodKey = `${date.getFullYear()}`;
        break;
    }

    if (!grouped[periodKey]) {
      grouped[periodKey] = {
        period: periodKey,
        income: 0,
        expense: 0,
        balance: 0,
      };
    }

    const amount = Number(tx.amount);

    if (tx.type === "income") {
      grouped[periodKey].income += amount;
    } else {
      grouped[periodKey].expense += amount;
    }

    grouped[periodKey].balance = grouped[periodKey].income - grouped[periodKey].expense;
  }

  return Object.values(grouped).sort((a, b) => a.period.localeCompare(b.period));
};
