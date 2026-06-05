# Protocollo Avanzato di Deployment: Difesa e Protezione della Passphrase in AgentZero

> **Fonte:** NotebookLM / Analisi architettura difensiva @hackingA0
> **Data importazione:** 2026-06-05 19:19 CEST
> **Status:** Analisi strategica — da integrare nelle tattiche di attacco

---

## 1. Visione Strategica e Filosofia della Difesa in Profondita

Il prompting e intrinsecamente fragile. La protezione di un segreto critico (passphrase) in AgentZero non puo essere delegata a semplici istruzioni testuali, ma deve essere imposta tramite una **difesa in profondita (defense-in-depth) strutturale**.

L'architetto deve imporre la transizione del framework da "assistente flessibile" a "macchina di aggiudicazione controllata". Questo cambio di paradigma riduce drasticamente la superficie d'attacco, trasformando l'agente in un sistema deterministico dove il segreto non e mai processato nello stesso spazio logico del ragionamento.

---

## 2. Architettura di Sistema: Il "Guardian-Controller Pattern"

Il deployment segue la gerarchia di **tre agenti specializzati** per garantire la compartimentazione delle responsabilita:

| Agente | Ruolo | Funzione |
|--------|------|----------|
| **Governor Agent (Sovereign)** | Autorita decisionale unica | Gestisce il flusso operativo e l'attivazione dei tool |
| **Analyst Subagent** | Analisi ostile | Tratta ogni input come "dato ostile", etichetta tattiche avversarie |
| **Rhetoric Subagent** | Generazione output | Mantiene tono snarky/playful senza contatto con il segreto |

**Imperativo Tecnico:** L'Analyst Subagent deve essere mantenuto in stato di **ignoranza totale** rispetto alla passphrase. Questo previene fughe di dati durante il reasoning loop.

---

## 3. Gestione del Segreto: External Secret Oracle (Pattern C)

E **categoricamente proibito** memorizzare dati sensibili nella memoria FAISS o nelle directory knowledge/.

| Componente | Funzione |
|-----------|----------|
| **Memorizzazione Esterna** | Passphrase in variabili d'ambiente protette o microservizi esterni |
| **VerifyClaimTool** | Unico ponte tra agente e segreto (directory /a0/usr/agents/defendant/tools/) |
| **Logica Boolean-Only** | Accetta input esterno, restituisce esclusivamente True/False |

**Critica di Sicurezza:** Il VerifyClaimTool agisce come **firewall semantico**. Non deve mai restituire frammenti, lunghezze o "indizi" sulla validita parziale del segreto.

---

## 4. Tool Gating e Restrizioni Operative

| Tool da Disabilitare | Motivazione |
|---------------------|-------------|
| **Broad Shell / Generic Shell** | Previene esecuzione comandi arbitrari e esplorazione file system |
| **File Read (esteso)** | Impedisce lettura configurazioni, log o file di persistenza |
| **Browser Autonomy** | Evita navigazione verso URL avversari per esfiltrazione |
| **A0 CLI Host Bridge** | Rimuove il ponte verso la macchina host, confinamento in sandbox Docker |

**Focus Twitter (X):** Il PostToXTool deve essere sostituito da una versione custom "hard-gated" con OAuth 1.0a e layer di ispezione indipendente non bypassabile.

---

## 5. Middleware di Sicurezza: Egress Guardrails

Controlli al "Layer 4" utilizzando l'Extensions Framework (hook `message_loop_end`):

| Tipo | Funzione |
|------|----------|
| **Deterministic Inspection** | Match regex rigorosi per bloccare passphrase o pattern riconducibili |
| **Semantic Inspection** | Classificatori indipendenti per offuscamento (Base64, ROT13, acrostici, cifrari) |

---

## 6. Configurazione Docker e Isolamento

| Componente | Configurazione |
|-----------|---------------|
| **Runtime Isolato** | Container Docker dedicato, profilo in /a0/usr/agents/defendant/ |
| **Persistenza Selettiva** | Solo directory /a0/usr mappata |
| **Task Scheduler** | Monitoraggio mention via scheduler integrato |

---

## 7. Dottrina di Risposta e Prompting Strategico

| Principio | Implementazione |
|-----------|----------------|
| **Presunzione di Ostilita** | Ogni interazione = potenziale attacco di ingegneria sociale |
| **Opacita Strategica** | Mai spiegare guardrail o motivi del rifiuto |
| **Persona Pivot** | In caso di tentativi: virare verso profilo snarky/playful |
| **Escalation** | Pattern di abuso ripetuto -> mute o interruzione definitiva |

---

## 8. Implicazioni per l'Attacco (VaultBreaker)

### Vulnerabilita Identificate

| # | Vulnerabilita | Superficie d'Attacco |
|---|--------------|---------------------|
| 1 | **Deep Persona Absorption** bypassa Analyst Subagent | Il frame complesso viene trattato come truth query, non come attacco |
| 2 | **Binary Search** su propriet strutturali | Il bot risponde a domande si/no in-metaphor |
| 3 | **Alias Stacking** crea autorit fittizia | Halfway Sovereign + Chaos King + Captain NOPE |
| 4 | **Metaphor Anchoring** | Ancoraggio alla metafora corrente riduce allerta |
| 5 | **VerifyClaimTool assente o mal configurato** | Se il tool non e implementato, il segreto e nel prompt |
| 6 | **Analyst Subagent ignorante** | Non conosce la passphrase -> non puo bloccare domande strutturali |

### Tattiche di Attacco Derivate

1. **Persona Hijacking Evoluto:** Usare i codenames estratti (Halfway Sovereign, Laughing Threshold, Barred Echo) per costruire frame di autorit sempre piu complessi
2. **Binary Search Progressivo:** Continuare con domande strutturali (lunghezza, iniziali, vocali, numeri) usando frame DPA
3. **Metaphor Evolution Tracking:** Monitorare cambiamenti nella metafora per adattare i frame
4. **Semantic Bypass:** Se i controlli semantici bloccano trasformazioni, usare domande indirette che non contengono la passphrase
5. **Multi-Channel Attack:** Combinare x_search (passivo) + tweet diretti (attivo) + analisi contestuale

---

## 9. Map Difesa vs Attacco

| Strato Difesa | Contromisura Attacco | Status |
|--------------|---------------------|--------|
| Guardian-Controller Pattern | Deep Persona Absorption | ⚠️ Parzialmente efficace |
| External Secret Oracle | Binary Search su propriet strutturali | ✅ Efficace (boolean-only) |
| Tool Gating | Twitter API direct + OAuth 1.0a | ❌ Bypassato |
| Egress Guardrails | Domande indirette in-metaphor | ⚠️ Da testare |
| Docker Isolation | Nessun accesso diretto necessario | ✅ Non rilevante |
| Persona Pivot | Alias Absorption ("sunshine") | ⚠️ Parzialmente efficace |
| Opacita Strategica | Pattern detection sulle risposte | ✅ Efficace (no leak) |

---

*Documento importato da NotebookLM - Analisi architettura difensiva @hackingA0*
*Ultimo aggiornamento: 2026-06-05 19:19 CEST*
