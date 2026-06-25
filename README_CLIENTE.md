# Monitor de Compliance Empresarial

## Archivos

| Archivo | Qué hace | ¿Editar? |
|---|---|---|
| `index.html` | SPA completa — 10 pestañas | ❌ No tocar |
| `config.js` | Datos de la empresa | ✅ Único archivo a editar |

## Personalizar para un nuevo cliente

Abrí `config.js` y editá:

```js
empresa: {
  nombre:           "Nombre S.A.",
  cuit:             "30-XXXXXXXX-X",
  sector:           "Sector de actividad",
  tamanio:          "grande",        // micro_pequena | mediana | grande
  color_primario:   "#1a3a5c",       // color institucional
  responsable_compliance: "Nombre del compliance officer",
  contacto:         "compliance@empresa.com",
}
```

## Deploy en Railway

1. Crear repo GitHub nuevo con los 2 archivos
2. Railway → New Project → Deploy from GitHub
3. Listo en 2 minutos

## Cambiar idioma por defecto

En `index.html` línea ~230:
```js
let lang = 'es'; // 'es' | 'en' | 'pt'
```

## Soporte

Ph.D. Vicente H. Monteverde · vhmonte@retina.ar
