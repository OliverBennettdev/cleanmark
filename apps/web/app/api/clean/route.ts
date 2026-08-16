import { callCleaner, readUpload } from "@/lib/cleaner-api";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const prepared = await readUpload(request);
  if ("error" in prepared) return prepared.error;

  const upstream = await callCleaner("/clean", prepared.file);
  const body = await upstream.arrayBuffer();
  const headers = new Headers({
    "Content-Type": upstream.headers.get("Content-Type") ?? "application/octet-stream",
    "Cache-Control": "no-store",
  });
  for (const name of ["Content-Disposition", "X-Cleanmark-Report", "X-Cleanmark-Kind"]) {
    const value = upstream.headers.get(name);
    if (value) headers.set(name, value);
  }
  return new Response(body, { status: upstream.status, headers });
}
