import request from "./api";

export function getAuditHistory(limit = 50) {
  return request(`/audit/history?limit=${limit}`);
}