export interface Transaction {
  id: number;
  title: string;
  amount: string;
  date: string;
  type: "income" | "expense" | "investment" | "loan" | "savings";
  description?: string | null;
}