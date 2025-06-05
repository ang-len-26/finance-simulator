import apiClient from "./apiClient";
import { Transaction } from "../types/Transaction";

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Transaction[];
}

// Obtener todas las transacciones (con paginación opcional)
export const fetchTransactions = async (page: number = 1): Promise<PaginatedResponse> => {
  const response = await apiClient.get(`/transactions/?page=${page}`);
  return response.data;
};

// Crear una nueva transacción
export const createTransaction = async (data: Transaction): Promise<Transaction> => {
  const response = await apiClient.post("/transactions/", data);
  return response.data;
};

// Obtener una transacción por ID
export const getTransactionById = async (id: number): Promise<Transaction> => {
  const response = await apiClient.get(`/transactions/${id}/`);
  return response.data;
};

// Actualizar una transacción
export const updateTransaction = async (id: number, data: Partial<Transaction>): Promise<Transaction> => {
  const response = await apiClient.put(`/transactions/${id}/`, data);
  return response.data;
};

// Eliminar una transacción
export const deleteTransaction = async (id: number): Promise<void> => {
  await apiClient.delete(`/transactions/${id}/`);
};
