// supabase/functions/get_by_id/index.ts
import { serve } from "https://deno.land/std@0.192.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY") ?? "";
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ✅ CORS headers (allow all origins for now — restrict in prod)
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "*",
  "Content-Type": "application/json",
};

serve(async (req) => {
  // ✅ Handle preflight OPTIONS request
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders,
    });
  }

  try {
    const { id } = await req.json();

    if (!id) {
      return new Response(
        JSON.stringify({ error: "Missing 'id' in request body" }),
        { status: 400, headers: corsHeaders }
      );
    }

    // Step 1: Fetch document record
    const { data: row, error: fetchError } = await supabase
      .from("shared_documents")
      .select("content")
      .eq("id", id)
      .single();

    if (fetchError || !row?.content) {
      return new Response(
        JSON.stringify({
          error: "Document not found",
          detail: fetchError?.message,
        }),
        { status: 404, headers: corsHeaders }
      );
    }

    const fileName = row.content.trim();

    // Step 2: Download from storage bucket
    const { data: fileData, error: downloadError } = await supabase.storage
      .from("documents")
      .download(fileName);

    if (downloadError || !fileData) {
      return new Response(
        JSON.stringify({
          error: "Failed to download file",
          detail: downloadError?.message,
        }),
        { status: 500, headers: corsHeaders }
      );
    }

    const fileText = await fileData.text();

    return new Response(JSON.stringify({ content: fileText }), {
      status: 200,
      headers: corsHeaders,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";

    return new Response(
      JSON.stringify({ error: "Internal Server Error", detail: message }),
      { status: 500, headers: corsHeaders }
    );
  }
});