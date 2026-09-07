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

export async function onRequestPut(context) {
  const id = context.params.id;
  let body;
  try {
    body = await context.request.json();
  } catch {
    return json({ ok: false, error: "Datos inválidos" }, 400);
  }

  const lista = await getAll(context.env);
  const idx = lista.findIndex((i) => i.id === id);
  if (idx === -1) {
    return json({ ok: false, error: "Incidencia no encontrada" }, 404);
  }

  lista[idx] = {
    ...lista[idx],
    ...body,
    id,
    actualizado: new Date().toISOString(),
  };
  await context.env.CALL_CENTER_KV.put(KEY, JSON.stringify(lista));

  return json({ ok: true, incidencia: lista[idx] });
}