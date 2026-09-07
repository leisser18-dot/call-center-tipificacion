const KEY = "incidencias";

async function getAll(env) {
  const raw = await env.CALL_CENTER_KV.get(KEY, "json");
  return Array.isArray(raw) ? raw : [];
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

export async function onRequestGet(context) {
  return json(await getAll(context.env));
}

export async function onRequestPost(context) {
  let body;
  try {
    body = await context.request.json();
  } catch {
    return json({ ok: false, error: "Datos inválidos" }, 400);
  }

  const incidencia = {
    id: crypto.randomUUID(),
    creado: new Date().toISOString(),
    ...body,
  };

  const lista = await getAll(context.env);
  lista.push(incidencia);
  await context.env.CALL_CENTER_KV.put(KEY, JSON.stringify(lista));

  return json({ ok: true, incidencia });
}