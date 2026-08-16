import "server-only";

export const MAX_FILE_BYTES = 25 * 1024 * 1024;
const SERVICE_URL = process.env.CLEANER_SERVICE_URL ?? "http://127.0.0.1:8765";

export type PreparedFile = { file: File } | { error: Response };

export async function readUpload(request: Request): Promise<PreparedFile> {
  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return { error: jsonError(400, "malformed", "Expected a multipart file upload.") };
  }
  const file = form.get("file");
  if (!(file instanceof File)) return { error: jsonError(400, "malformed", "Missing file field.") };
  if (file.size > MAX_FILE_BYTES) return { error: jsonError(413, "too-large", "File exceeds the 25 MiB limit.") };
  return { file };
}

export function jsonError(status: number, code: string, message: string) {
  return Response.json({ ok: false, error: { code, message } }, { status, headers: { "Cache-Control": "no-store" } });
}

export async function callCleaner(path: "/inspect" | "/clean", file: File): Promise<Response> {
  const form = new FormData();
  form.append("file", file, file.name);
  try {
    return await fetch(`${SERVICE_URL}${path}`, {
      method: "POST",
      body: form,
      cache: "no-store",
      signal: AbortSignal.timeout(90_000),
    });
  } catch {
    return jsonError(503, "service-unavailable", "Cleaner service is unavailable.");
  }
}
