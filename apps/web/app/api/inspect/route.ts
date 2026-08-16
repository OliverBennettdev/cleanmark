import { callCleaner, readUpload } from "@/lib/cleaner-api";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const prepared = await readUpload(request);
  if ("error" in prepared) return prepared.error;

  const upstream = await callCleaner("/inspect", prepared.file);
  const body = await upstream.arrayBuffer();
  return new Response(body, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("Content-Type") ?? "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
