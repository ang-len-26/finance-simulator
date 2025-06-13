export interface Transaction {
  id: number;
  title: string;
  amount: number; 
  date: string;
  type: "income" | "expense" | "investment" | "loan" | "savings";
  description?: string | null;
}