import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.49.3";

const SUP_URL = Deno.env.get("_SUPABASE_URL")!;
const SUP_KEY = Deno.env.get("_SUPABASE_KEY")!;
const supabase = createClient(SUP_URL, SUP_KEY);

// ✅ CORS headers
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "*",
  "Content-Type": "application/json",
};

Deno.serve(async (req) => {
  // ✅ Handle preflight OPTIONS request
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  try {
    const { id, fileContent, language } = await req.json();

    if (!id || !fileContent) {
      return new Response(
        JSON.stringify({ message: "Document ID and fileContent are required" }),
        { status: 400, headers: corsHeaders },
      );
    }

    // Step 1: Get file name from DB
    const { data: docData, error: fetchErr } = await supabase
      .from("shared_documents")
      .select("content")
      .eq("id", id)
      .single();

    if (fetchErr || !docData?.content) {
      return new Response(
        JSON.stringify({
          message: "Document not found",
          error: fetchErr?.message,
        }),
        { status: 404, headers: corsHeaders },
      );
    }

    const fileName = docData.content.trim();

    // Step 2: Upload file to bucket
    const fileBlob = new Blob([fileContent], { type: "text/plain" });

    const { error: uploadError } = await supabase.storage
      .from("documents")
      .upload(fileName, fileBlob, {
        upsert: true,
      });

    if (uploadError) {
      return new Response(
        JSON.stringify({
          message: "Failed to upload file",
          error: uploadError.message,
        }),
        { status: 500, headers: corsHeaders },
      );
    }

    // Step 3: Update metadata
    const { error: updateError } = await supabase
      .from("shared_documents")
      .update({
        language: language || "plaintext",
        last_updated: new Date().toISOString(),
      })
      .eq("id", id);

    if (updateError) {
      return new Response(
        JSON.stringify({
          message: "Updated file, but failed to update metadata",
          error: updateError.message,
        }),
        { status: 500, headers: corsHeaders },
      );
    }

    return new Response(
      JSON.stringify({
        message: "Document updated successfully",
        file: fileName,
      }),
      { status: 200, headers: corsHeaders },
    );
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : "Unknown error";

    return new Response(
      JSON.stringify({ message: "Internal Server Error", error: errorMessage }),
      { status: 500, headers: corsHeaders },
    );
  }
});