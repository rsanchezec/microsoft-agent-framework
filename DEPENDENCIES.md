# 📦 Gestión de Dependencias

## 🎯 Archivos de Requirements

Este proyecto tiene dos archivos de requirements con diferentes propósitos:

### 1. `requirements.txt` - Versiones Exactas (PRODUCCIÓN)

```txt
agent-framework==1.0.0b251114
agent-framework-devui==1.0.0b251120
```

**✅ Ventajas:**
- Reproducible: siempre instala las mismas versiones
- Seguro: no hay sorpresas de breaking changes
- Recomendado para: **producción, CI/CD, despliegues**

**❌ Desventajas:**
- No recibe actualizaciones automáticas
- Tienes que actualizar manualmente

**Uso:**
```bash
pip install -r requirements.txt
```

---

### 2. `requirements-flexible.txt` - Versiones Flexibles (DESARROLLO)

```txt
agent-framework>=1.0.0b251114,<2.0.0
agent-framework-devui>=1.0.0b251120,<2.0.0
```

**✅ Ventajas:**
- Permite actualizaciones de parches (1.0.1, 1.0.2)
- Permite actualizaciones menores (1.1.0, 1.2.0)
- Recibes bug fixes automáticamente

**❌ Desventajas:**
- Menos reproducible
- Puede introducir cambios inesperados

**Uso:**
```bash
pip install -r requirements-flexible.txt
```

---

## 🔄 Cómo Actualizar Dependencias

### Opción A: Actualización Manual Segura (Recomendado)

1. **Ver versiones disponibles:**
   ```bash
   pip index versions agent-framework
   ```

2. **Actualizar a versión específica:**
   ```bash
   pip install agent-framework==1.0.0b251201
   pip install agent-framework-devui==1.0.0b251201
   ```

3. **Probar que todo funcione:**
   ```bash
   python 001_createandrunanagent.py
   python 012_sequential_workflow.py
   # etc.
   ```

4. **Si funciona, actualizar requirements.txt:**
   ```bash
   # Manualmente editar el archivo
   # O usar pip freeze (cuidado, incluye TODAS las dependencias)
   pip freeze | grep agent-framework > requirements.txt
   ```

### Opción B: Actualización Automática (Solo desarrollo)

```bash
pip install --upgrade agent-framework agent-framework-devui
```

⚠️ **Advertencia:** Esto puede romper tu código si hay breaking changes.

---

## 📊 Tabla de Estrategias

| Estrategia | Formato | Ejemplo | Cuándo Usar |
|------------|---------|---------|-------------|
| **Versión Exacta** | `package==X.Y.Z` | `agent-framework==1.0.0b251114` | Producción, CI/CD |
| **Rango Compatible** | `package>=X.Y.Z,<MAJOR.0.0` | `agent-framework>=1.0.0,<2.0.0` | Desarrollo |
| **Versión Mínima** | `package>=X.Y.Z` | `agent-framework>=1.0.0` | Solo experimentación |
| **Sin Versión** | `package` | `agent-framework` | ❌ Nunca (no reproducible) |

---

## 🚨 Problemas Comunes

### Problema 1: "Breaking Changes"

**Síntoma:** El código funcionaba ayer, hoy no.

**Causa:** Actualización automática a versión incompatible.

**Solución:**
```bash
# Volver a versión conocida
pip install agent-framework==1.0.0b251114

# Actualizar requirements.txt con versión exacta
```

### Problema 2: "Funciona en mi máquina, no en producción"

**Síntoma:** Desarrollo funciona, producción falla.

**Causa:** Diferentes versiones instaladas.

**Solución:**
```bash
# Usar requirements.txt con versiones exactas
# Tanto en dev como en prod
pip install -r requirements.txt
```

### Problema 3: "pip freeze incluye demasiadas cosas"

**Síntoma:** `pip freeze` genera 100+ líneas.

**Causa:** Incluye dependencias transitivas.

**Solución:**
```bash
# Solo dependencias directas (manual)
echo "agent-framework==1.0.0b251114" > requirements.txt
echo "agent-framework-devui==1.0.0b251120" >> requirements.txt

# O usar pipreqs (instalar primero: pip install pipreqs)
pipreqs . --force
```

---

## 💡 Mejores Prácticas

### ✅ DO (Hacer):

1. **Usar versiones exactas en producción**
   ```txt
   agent-framework==1.0.0b251114
   ```

2. **Documentar por qué usas una versión específica**
   ```txt
   # Versión 1.0.0b251114: última versión estable antes de breaking change
   agent-framework==1.0.0b251114
   ```

3. **Tener un ambiente de testing**
   ```bash
   # Test environment: prueba actualizaciones aquí primero
   pip install agent-framework==1.0.0b251201
   # Si pasa todos los tests, actualiza producción
   ```

4. **Commit requirements.txt al repositorio**
   ```bash
   git add requirements.txt
   git commit -m "Pin agent-framework to 1.0.0b251114"
   ```

### ❌ DON'T (No Hacer):

1. **No usar versiones sin especificar**
   ```txt
   agent-framework  # ❌ Mala idea
   ```

2. **No actualizar sin probar**
   ```bash
   pip install --upgrade agent-framework  # ❌ En producción
   ```

3. **No mezclar estrategias**
   ```txt
   agent-framework==1.0.0  # ✅ Exacta
   other-package>=1.0.0    # ❌ Flexible
   # Inconsistente, confuso
   ```

---

## 🔍 Verificar Versiones Instaladas

```bash
# Ver versión de un paquete específico
pip show agent-framework

# Ver todas las versiones instaladas
pip list

# Buscar paquetes de agent-framework
pip list | grep agent-framework

# Generar requirements con versiones actuales
pip freeze | grep agent-framework
```

---

## 📚 Referencias

- [Semantic Versioning](https://semver.org/) - Entender versionado X.Y.Z
- [pip Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)

---

**Última actualización:** 2024-12-10
**Versiones actuales:** agent-framework==1.0.0b251114, agent-framework-devui==1.0.0b251120
