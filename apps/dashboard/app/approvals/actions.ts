"use server";

import { revalidatePath } from "next/cache";
import { apiPost } from "../../lib/api";

export async function approveAction(formData: FormData) {
  const id = formData.get("id");
  await apiPost(`/approvals/${id}/approve`, { approved_by: "dashboard" });
  revalidatePath("/approvals");
}

export async function rejectAction(formData: FormData) {
  const id = formData.get("id");
  await apiPost(`/approvals/${id}/reject`, { approved_by: "dashboard" });
  revalidatePath("/approvals");
}
