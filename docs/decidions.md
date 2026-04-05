# Architectural & Technical Decisions

Este documento registra as principais decisões arquiteturais e técnicas tomadas durante o desenvolvimento do projeto **Incident Decision Engine**.

O objetivo é tornar explícito **o raciocínio por trás da arquitetura**, facilitando manutenção, evolução futura e entendimento por outros desenvolvedores.

---

## ADR-001 — Adoção de Arquitetura em Camadas (inspirada em Clean Architecture)

**Status:** Aprovado  
**Contexto:**  
O projeto foi criado com foco em estudo e prática de engenharia de software, exigindo uma estrutura que favorecesse separação de responsabilidades, testabilidade e evolução.

**Decisão:**  
Adotar uma arquitetura em camadas, inspirada nos princípios de Clean Architecture, separando:
- Interface (UI)
- Orquestração de decisão (Decision Engine)
- Regras de negócio (Domain)
- Infraestrutura (I/O)

**Consequências:**
- ✅ Regras de negócio ficam isoladas de frameworks e interfaces
- ✅ Baixo acoplamento entre camadas
- ✅ Facilidade para evoluir UI ou formatos de entrada
- ❌ Estrutura inicial mais complexa que uma solução monolítica simples

---

## ADR-002 — Criação de um Decision Engine centralizado

**Status:** Aprovado  
**Contexto:**  
A lógica de decisão não deveria estar espalhada pela interface ou por componentes de infraestrutura.

**Decisão:**  
Criar um **Decision Engine** responsável por orquestrar:
- Validação de dados
- Aplicação de regras
- Geração da decisão final

**Consequências:**
- ✅ Centralização da lógica de decisão
- ✅ Maior clareza no fluxo do sistema
- ✅ Reutilização do motor em diferentes interfaces
- ❌ Camada adicional de abstração

---

## ADR-003 — Modelagem explícita do Domínio

**Status:** Aprovado  
**Contexto:**  
O sistema lida com conceitos claros de negócio, como incidentes, SLAs e decisões.

**Decisão:**  
Modelar explicitamente o domínio através de entidades como:
- Incident
- SLA
- Decision

Essas entidades não dependem de interface ou infraestrutura.

**Consequências:**
- ✅ Código mais expressivo e legível
- ✅ Regras de negócio melhor encapsuladas
- ✅ Maior facilidade para criar testes
- ❌ Necessidade de maior disciplina na separação de responsabilidades

---

## ADR-004 — Uso de JSON e CSV como formatos de entrada e saída

**Status:** Aprovado  
**Contexto:**  
O projeto precisava trabalhar com dados simples, genéricos e compatíveis com cenários reais de ITSM.

**Decisão:**  
Utilizar **JSON e CSV** como formatos de entrada e saída, tratados pela camada de infraestrutura.

**Consequências:**
- ✅ Simplicidade e compatibilidade com ferramentas externas
- ✅ Fácil adaptação para exportações futuras (ex: API)
- ✅ Nenhuma dependência de serviços externos
- ❌ Não otimizado para processamento em larga escala

---

## ADR-005 — Uso de Tkinter para Interface Gráfica

**Status:** Aprovado  
**Contexto:**  
O foco do projeto é arquitetura e regras de negócio, não desenvolvimento web.

**Decisão:**  
Utilizar **Tkinter** como interface gráfica simples para interação com o usuário.

**Consequências:**
- ✅ Baixa complexidade
- ✅ Não adiciona dependências externas
- ✅ Mantém foco na arquitetura
- ❌ Interface visual simples
- ❌ Não voltada para uso produtivo

---

## Considerações Finais

As decisões documentadas neste arquivo refletem **escolhas conscientes**, priorizando:
- Clareza arquitetural
- Evolução do sistema
- Valor educacional e de portfólio

Este documento deve evoluir junto com o projeto, registrando novas decisões conforme a complexidade aumenta.