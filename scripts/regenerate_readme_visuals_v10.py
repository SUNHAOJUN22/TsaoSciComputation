from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUAL_ROOT = ROOT / "assets" / "visuals"
SYSTEM_ID = "uiux-pro-max-scientific-swiss-v1"

TOKENS = {
    "canvas": "#0B1220",
    "surface": "#111827",
    "raised": "#172033",
    "border": "#334155",
    "text": "#F8FAFC",
    "secondary": "#CBD5E1",
    "muted": "#94A3B8",
    "blue": "#3B82F6",
    "cyan": "#06B6D4",
    "teal": "#14B8A6",
    "green": "#22C55E",
    "amber": "#F59E0B",
    "orange": "#F97316",
    "red": "#EF4444",
}


@dataclass(frozen=True, slots=True)
class VisualSpec:
    filename: str
    family: str
    title: str
    description: str
    heading: str
    subtitle: str
    accent: str
    icon: str
    stages: tuple[tuple[str, str], ...]
    footer: str


RAW_SPECS = """
hero-multiscale.svg|architecture|TsaoSciComputation multiscale evidence architecture|A structured scientific workflow from electronic structure through industrial process decisions with explicit evidence gates.|From electrons to industrial decisions|One orchestration layer connects scales without confusing numerical completion with scientific acceptance.|cyan|orbit|Electron~density · charge · wavefunction;Atom~structure · force · spectrum;Molecule~ensemble · reaction · free energy;Material~morphology · interface · fields;Process~reactor · plant · reviewed decision|Every scale handoff preserves units, provenance, uncertainty, applicability and review authority.
agent-orchestration.svg|architecture|Governed scientific agent orchestration|A governed agent separates intent, contracts, routing, execution evidence and qualified review.|Governed scientific agent|Planning and execution remain auditable, bounded and fail-closed.|blue|network|Intent~question · claim · observable;Contract~inputs · units · acceptance;Route~scale · method · workflow;Execute~preflight · bounded run;Review~evidence · domain · authority|Automation stops when required evidence, applicability or human authorization is missing.
capability-landscape.svg|architecture|Scientific capability landscape|Capabilities, workflows, adapters, evidence and governance are organized as separate layers.|Capability system landscape|A clear hierarchy prevents catalog entries from becoming unsupported execution claims.|teal|layers|Capabilities~164 scoped contracts;Workflows~20 governed programs;Adapters~27 conservative interfaces;Evidence~tests · hashes · reports;Governance~policy · review · release|Declared capability, available software and validated live execution are distinct states.
quantum-to-md.svg|quantum|Electronic structure to molecular dynamics handoff|Electronic calculations become molecular simulation inputs through qualified parameterization and validation.|Quantum to molecular simulation|Cross-scale transfer requires semantic, unit and uncertainty contracts.|blue|molecule|Electronic~method · basis · state;Parameterize~charges · bonded terms;Build~composition · boundary;Sample~ensemble · replicas;Validate~observable · convergence|A force field is accepted only for the state space and observables it was validated against.
electronic-structure-landscape.svg|quantum|Electronic structure evidence landscape|Geometry, self-consistency, energy, forces and observables are checked through separate evidence gates.|Electronic structure evidence|Convergence is necessary but not sufficient for a physical electronic-structure claim.|cyan|orbit|Geometry~symmetry · constraints;SCF~threshold · stability;Energy~reference · correction;Forces~stationarity · stress;Observable~density · band · response|Method fitness, numerical stability and observable validation remain explicit.
free-energy-sampling.svg|quantum|Enhanced sampling and free energy workflow|Collective variables, biased sampling, overlap, reconstruction and uncertainty support a bounded free-energy claim.|Enhanced sampling and free energy|Sampling quality is judged by overlap and reproducibility, not by a smooth curve alone.|teal|chart|Coordinate~CV definition · relevance;Bias~protocol · strength;Sample~replicas · transitions;Reconstruct~weights · overlap;Uncertainty~blocks · sensitivity|A reconstructed landscape is rejected when state overlap or convergence evidence is inadequate.
reaction-kinetics-network.svg|reaction|Reaction pathway and kinetic network|Stationary states, transition states, rates, networks and reactor handoffs are validated in sequence.|Reaction pathways and kinetics|Energetics become kinetics only after state, rate and network consistency checks.|orange|network|States~reactants · products;Transition~mode · connectivity;Rates~thermo · tunneling;Network~balance · stiffness;Reactor~transport · conditions|A plausible pathway does not establish dominant kinetics under reactor conditions.
ml-potential-active-learning.svg|reaction|Machine learned potential active learning|Reference labels, committee uncertainty, exploration and validation form a bounded active-learning loop.|ML potentials and active learning|Model uncertainty controls data acquisition and the permitted simulation domain.|green|network|Labels~reference method · diversity;Train~split · loss · regularize;Committee~disagreement · alarm;Explore~sample · query · enrich;Accept~forces · dynamics · domain|Low test error alone cannot authorize extrapolative dynamics.
polymer-process.svg|materials|Polymer structure to process workflow|Molecular sequence and morphology connect to constitutive response, process flow and product evidence.|Polymer to process handoff|Each scale transfers defined observables rather than informal qualitative impressions.|teal|flow|Sequence~composition · topology;Morphology~crystal · phase · interface;Constitutive~rheology · transport;Flow~history · cooling · stress;Product~quality · uncertainty|Process predictions require validated constitutive laws and realistic thermal histories.
mesoscale-phase-field.svg|materials|Mesoscale phase field evidence workflow|Coarse graining, field construction, evolution, morphology metrics and continuum transfer are validated separately.|Mesoscale morphology evolution|Topology metrics and cross-scale transfer remain evidence-bearing outputs.|cyan|layers|Coarse grain~variables · mapping;Field model~free energy · mobility;Evolve~mesh · time · stability;Metrics~domains · connectivity;Handoff~tensor · uncertainty|A visually plausible morphology is not accepted without convergence and metric evidence.
continuum-multiphysics.svg|continuum|Continuum multiphysics verification|Geometry, discretization, coupled fields, numerical solution and verification define a continuum claim.|CFD FEM and multiphysics|Mesh quality, conservation and coupling evidence remain independent gates.|blue|flow|Domain~geometry · boundary;Discretize~mesh · elements;Couple~heat · flow · mechanics;Solve~residual · stability;Verify~balance · refinement|Residual convergence does not replace mesh, conservation and model-form verification.
process-optimization-uq.svg|process|Process optimization and uncertainty workflow|Flowsheet construction, calibration, uncertainty, constrained optimization and human authorization are separated.|Process optimization with UQ|A numerical optimum must survive feasibility, uncertainty and safety review.|amber|chart|Flowsheet~units · properties · recycle;Calibrate~data · discrepancy;Uncertainty~inputs · propagation;Optimize~constraints · Pareto;Authorize~safety · applicability|Optimization output remains a candidate until qualified engineering review.
uncertainty-sensitivity.svg|observables|Uncertainty and sensitivity decision workflow|Input distributions, propagation, sensitivity ranking, intervals and robust decisions are distinguished.|Uncertainty and sensitivity|Sensitivity explains influence; uncertainty bounds confidence and decision robustness.|amber|chart|Inputs~distribution · correlation;Propagate~sampling · surrogate;Rank~global · interaction;Interval~prediction · confidence;Decide~robustness · threshold|Point predictions are insufficient when uncertainty changes the decision.
electrochemical-interface.svg|materials|Electrochemical interface evidence workflow|Surface state, double-layer assumptions, charge transfer, transport and observables form an electrochemical claim.|Electrochemical interfaces|Electronic, interfacial and transport descriptions require compatible conditions.|cyan|layers|Surface~termination · potential;Double layer~ions · solvent · field;Transfer~barrier · kinetics;Transport~diffusion · migration;Observe~current · spectrum · domain|A single interfacial energy cannot establish device-scale electrochemical performance.
spectroscopy-observables.svg|observables|Spectroscopy observable assignment workflow|State models, transition rules, instrument response, assignment and confidence support spectral interpretation.|Spectroscopy observables|Calculated transitions become assignments only after instrument and uncertainty checks.|blue|spectrum|States~method · population;Transitions~selection · intensity;Instrument~broadening · resolution;Assign~peak · mixture · alternative;Confidence~fit · evidence · domain|Spectral agreement must include competing assignments and experimental response.
transport-degradation.svg|materials|Coupled transport and degradation workflow|Charge, heat and species transport couple to damage kinetics and bounded lifetime evidence.|Transport and degradation|Accelerated conditions require explicit scale and mechanism validity.|orange|flow|Fields~charge · heat · species;Kinetics~reaction · damage;Couple~feedback · boundary;Accelerate~stress · temperature;Lifetime~interval · applicability|Extrapolated lifetime is rejected when degradation mechanism or domain changes.
inverse-design-loop.svg|observables|Inverse design evidence loop|Traceable targets, constrained generation, screening, Pareto validation and human choice govern inverse design.|Inverse design with constraints|Generated candidates remain hypotheses until multi-fidelity validation.|green|network|Targets~observable · tolerance;Generate~representation · constraint;Screen~surrogate · uncertainty;Pareto~tradeoff · robustness;Select~validate · review · choose|Optimization novelty does not replace manufacturability, safety or domain review.
data-model-governance.svg|governance|Scientific data and model governance|Ingestion, transformations, versioning, access control and release gates preserve scientific lineage.|Data and model governance|Every transformation and model release remains traceable and reviewable.|teal|shield|Ingest~source · consent · checksum;Transform~schema · units · lineage;Version~data · model · code;Control~access · policy · audit;Release~evidence · approval · rollback|Untraceable data or model changes block release regardless of predictive score.
reactor-safety-control.svg|operations|Reactor safety control workflow|Balances, state estimation, control and independent protection layers define bounded operational authority.|Reactor safety and control|Control performance and independent protection remain separate safety claims.|red|shield|Balances~mass · energy · inventory;Estimate~sensor · soft state;Control~constraint · response;Protect~alarm · trip · relief;Authorize~scenario · margin · role|A stable controller is not an independent protection layer.
hpc-execution-provenance.svg|operations|Bounded HPC execution provenance|Environment qualification, scheduler submission, isolated execution, artifact hashing and review preserve run evidence.|HPC execution provenance|Compute automation remains bounded by environment, resource and provenance contracts.|teal|hpc|Preflight~software · license · resource;Submit~scheduler · queue · limits;Execute~isolation · timeout · seed;Hash~input · output · log;Review~status · evidence · retain|A completed job is not a validated scientific result.
engine-ecosystem.svg|architecture|Scientific solver adapter ecosystem|Declared engines, environment discovery, probes, conservative parsing and certification define adapter trust.|Solver-aware adapter ecosystem|External engines remain optional, separately licensed and independently validated.|cyan|network|Declare~interface · executable;Discover~path · module · version;Probe~environment · capability;Parse~status · failure · convergence;Certify~fixture · live evidence · scope|An adapter definition does not prove local availability or live execution.
evidence-loop.svg|architecture|Fail-closed scientific evidence loop|Contract, execution, convergence, physics and acceptance checks form a fail-closed loop.|Scientific acceptance loop|Each gate may stop the workflow and preserve the evidence for review.|green|shield|Contract~claim · observable · criteria;Run~bounded · logged · hashed;Converge~numerical · repeatable;Validate~physical · benchmark;Accept~uncertainty · domain · review|Completed is not parsed, converged, validated or accepted.
confidence-ladder.svg|architecture|Scientific confidence ladder C0 to C5|Confidence levels connect stronger claims to progressively stronger evidence and explicit authorization.|C0 to C5 confidence ladder|Confidence is evidence-specific and cannot be inferred from presentation quality.|amber|layers|C0~declared · unverified;C1~fixture · static check;C2~reference · benchmark;C3~independent reproduction;C4-C5~live evidence · explicit authority|Higher confidence requires stronger independent evidence, not more assertive wording.
digital-thread.svg|architecture|Reproducible scientific digital thread|Inputs, environment, execution, artifacts and release evidence form a reproducible digital thread.|Reproducible digital thread|Hashes and semantic metadata connect every governed handoff.|blue|flow|Inputs~contract · units · seed;Environment~versions · licenses;Execution~commands · resources;Artifacts~raw · parsed · checksums;Release~SBOM · manifest · provenance|Documentation supports but does not replace byte-level reproducibility evidence.
periodic-materials-stability.svg|reaction|Periodic materials stability workflow|Cell relaxation, convergence, defects, phonons and observables support a bounded periodic-material claim.|Periodic materials stability|Finite-size and dynamical stability checks remain explicit.|cyan|lattice|Cell~symmetry · relaxation;Converge~k-point · cutoff;Defect~charge · chemical potential;Phonon~imaginary mode · supercell;Observe~band · DOS · stability|A relaxed cell alone cannot establish thermodynamic or dynamical stability.
catalysis-microkinetics.svg|reaction|Catalysis microkinetic evidence workflow|Active sites, elementary steps, thermodynamic closure, coverage and rate control support catalyst ranking.|Catalysis and microkinetics|Site identity, coverage effects and reactor conditions remain explicit.|orange|network|Site~structure · state · coverage;Steps~elementary · reversible;Thermo~closure · reference;Coverage~interaction · occupancy;Rate~TOF · control · sensitivity|A low isolated barrier does not guarantee catalytic activity or selectivity.
polymerization-population-balance.svg|materials|Polymerization population balance workflow|Elementary chain events, moments, distributions, parameter identifiability and population balances support polymerization claims.|Polymerization and PBE|Moments and distributions must remain consistent with chain-event kinetics.|teal|network|Initiate~sites · activation;Propagate~monomer · sequence;Transfer~hydrogen · comonomer;Moments~Mn · Mw · composition;PBE~distribution · closure · fit|Matching conversion alone does not identify molecular architecture.
extrusion-rheology-window.svg|materials|Extrusion rheology processing window|Constitutive rheology, screw and die flow, residence time, thermal history and product quality define a process window.|Extrusion rheology window|Material history and geometry constrain the usable processing region.|amber|process|Rheology~shear · extension · temperature;Screw~mixing · pressure · torque;Residence~RTD · degradation;Thermal~heating · cooling · crystallize;Window~throughput · quality · margin|A single viscosity curve cannot establish a robust extrusion window.
digital-twin-drift.svg|governance|Digital twin drift aware lifecycle|Scope, state estimation, online updating, drift detection and decision authority govern a digital twin.|Digital twin lifecycle|Online adaptation is bounded by applicability and review policy.|blue|control|Scope~asset · state · observable;Estimate~sensor · residual · UQ;Update~parameter · cadence · audit;Drift~distribution · performance;Authority~advice · control · escalation|A digital twin must detect when it no longer represents the asset.
fem-verification-convergence.svg|continuum|Finite element verification and convergence|Governing equations, weak form, mesh and time-step convergence, and balance checks support FEM evidence.|FEM verification|Discretization choices remain part of the scientific claim.|blue|lattice|Equations~domain · constitutive;Weak form~spaces · boundary;Mesh~quality · refinement;Time step~stability · order;Balance~residual · conservation|A visually smooth field is not evidence of discretization convergence.
scale-multifidelity-plan.svg|observables|Scientific scale and multi fidelity plan|Claims, scale boundaries, method fitness, fidelity ladders and evidence budgets structure a calculation program.|Scale and multi-fidelity planning|The cheapest model is used only within a declared decision role.|amber|layers|Claim~question · observable;Scale~electronic · continuum;Method~fitness · assumptions;Fidelity~screen · refine · verify;Budget~cost · evidence · stop|Higher fidelity is targeted where it changes uncertainty or decisions.
quantum-chemistry-thermochemistry.svg|quantum|Quantum chemistry thermochemistry workflow|Conformer coverage, optimization, frequencies, solvation and thermal corrections support molecular free energies.|Quantum chemistry and thermochemistry|Electronic energy and Gibbs free energy are not interchangeable.|cyan|molecule|Conformers~search · rank · coverage;Optimize~state · symmetry · constraints;Frequency~minimum · transition;Solvation~model · standard state;Gibbs~ZPE · entropy · uncertainty|Thermochemical claims require state, temperature and standard-state consistency.
molecular-dynamics-transport.svg|quantum|Molecular dynamics transport workflow|System qualification, equilibration, production sampling, transport analysis and convergence define MD evidence.|Molecular dynamics and transport|Trajectory length is judged against observable convergence and independent replicas.|teal|flow|Build~composition · force field;Equilibrate~NVT · NPT · density;Produce~ensemble · replica · seed;Analyze~diffusion · RDF · chain;Converge~blocks · finite size · domain|One long trajectory cannot replace independent convergence evidence.
polymer-composite-topology.svg|materials|Polymer composite topology workflow|Interface construction, dispersion, percolation, coupled response and property maps connect topology to performance.|Polymer composite topology|Connectivity and interface state remain distinct structural variables.|green|network|Interface~chemistry · adhesion;Disperse~localize · aggregate;Percolate~threshold · network;Couple~mechanical · electrical;Map~structure · property · domain|A filler fraction alone cannot define topology or transport pathways.
flowsheet-convergence-balances.svg|process|Flowsheet convergence and balance workflow|Property methods, unit operations, recycle convergence, material and energy balances, and optimization form a process model.|Flowsheet convergence and balances|Recycle convergence is checked separately from physical balance closure.|amber|process|Properties~components · phase model;Units~reactor · separator · exchanger;Recycle~tear · initialize · converge;Balances~mass · energy · element;Optimize~constraint · uncertainty · review|A converged flowsheet is rejected when balances or property methods are unsuitable.
multiscale-handoff-uncertainty.svg|observables|Multiscale handoff and uncertainty workflow|Observable semantics, units, provenance, uncertainty and receiving-model validation govern cross-scale transfer.|Multiscale handoff contracts|Every receiving model must confirm the meaning and domain of transferred parameters.|blue|flow|Observable~definition · averaging;Units~basis · normalization;Provenance~method · state · version;Uncertainty~distribution · covariance;Receive~map · validate · reject|Cross-scale numbers without semantic contracts are not transferable evidence.
conformer-solvation-excited-state.svg|quantum|Conformer solvation and excited state workflow|Conformer search, solvent conditions, excited states, thermal populations and observables support molecular-state claims.|Molecular states and environments|Populations and environments remain explicit parts of the observable.|cyan|molecule|Search~coverage · deduplicate · rank;Solvent~model · ionic state;Excited~roots · character · method;Thermal~ZPE · entropy · population;Observe~spectrum · kinetics · domain|A single optimized structure cannot support ensemble or solution claims.
surface-adsorption-migration.svg|reaction|Surface adsorption defect and migration workflow|Slab construction, adsorption references, charged defects, migration paths and corrections support surface mechanisms.|Surfaces defects and migration|Reference states and finite-size effects remain part of the barrier claim.|orange|lattice|Slab~termination · vacuum · layers;Adsorb~site · coverage · reference;Defect~charge · chemical potential;Migrate~NEB · images · barrier;Correct~finite size · rate · domain|Adsorption and migration rankings are rejected when references are unresolved.
cfd-turbulence-multiphase.svg|continuum|CFD turbulence multiphase transport workflow|Geometry, closure models, phase regimes, coupled transport and conservation support CFD evidence.|CFD closures and transport|Flow regime and mesh evidence remain independent of residual history.|cyan|flow|Geometry~domain · BC · mesh;Closure~laminar · turbulence;Phases~interface · slip · regime;Transport~heat · species · reaction;Conserve~mass · energy · sensitivity|Residual convergence does not establish regime or grid independence.
reactor-scaleup-thermal-risk.svg|process|Reactor scale up and thermal risk workflow|Ideal baselines, residence-time behavior, heat removal, scale transfer and safety margins support reactor scale-up.|Reactor scale-up and thermal risk|Kinetics, transport and protection assumptions are qualified independently.|red|process|Baseline~batch · CSTR · PFR;RTD~mixing · bypass · dispersion;Thermal~release · removal · runaway;Scale~geometry · transfer · fit;Margin~scenario · protection · review|A fitted conversion curve cannot authorize scale-up or dismiss runaway risk.
dynamic-control-estimation.svg|operations|Dynamic control and state estimation workflow|Dynamic states, operating sequences, control structures, estimators and safety boundaries define operational evidence.|Dynamic control and estimation|Control performance and safety authority remain separate.|blue|control|States~inventory · sensor · units;Sequence~startup · shutdown · modes;Control~PID · constraint · interaction;Estimate~soft sensor · residual · UQ;Boundary~disturbance · trip · authority|A stable controller cannot replace independent safety protection.
hpc-failure-recovery.svg|operations|HPC failure classification and recovery workflow|Preflight, checkpoint integrity, failure classification, bounded retries and escalation govern automated recovery.|HPC failure and recovery|Recovery is limited by reproducibility, retry budgets and preserved artifacts.|teal|hpc|Preflight~software · license · resource;Checkpoint~state · hash · restart;Classify~input · solver · system;Retry~bounded · changed parameter;Escalate~package · preserve · review|Unknown failures, corrupted checkpoints or repeated divergence stop automation.
""".strip()


README_EN_BLOCK = """<!-- VISUAL_SYSTEM_V10:START -->
> **Visual system V10.** All 42 repository-local diagrams now follow a UI/UX Pro Max-derived **Scientific Swiss Bento** system: high contrast, systematic spacing, semantic accents, numbered stages, consistent line language and explicit evidence boundaries. The SVGs remain static, self-contained and accessible; they are explanatory architecture diagrams, not solver screenshots or fabricated scientific plots. See [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- VISUAL_SYSTEM_V10:END -->"""

README_ZH_BLOCK = """<!-- VISUAL_SYSTEM_V10:START -->
> **视觉系统 V10。** 全部 42 幅仓库本地配图现已统一采用源自 UI/UX Pro Max 方法的 **Scientific Swiss Bento** 体系：高对比度、系统化间距、语义色、编号阶段、统一线条语言及明确的证据边界。所有 SVG 均为静态、自包含、可访问的解释图，不是求解器截图，也不伪造科研曲线。详见 [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md)。
<!-- VISUAL_SYSTEM_V10:END -->"""

VISUAL_POLICY_BLOCK = """## UI/UX Pro Max design system

The atlas follows [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md): Scientific Swiss minimalism, Bento information hierarchy, an 8 px spacing rhythm, system typography, semantic non-purple accents, consistent 2 px strokes, and color-independent numbered stages. Decorative AI gradients, neon glow, emoji icons and external resources are prohibited.
"""


VISUAL_MARKER = re.compile(
    r"<!-- VISUAL_SYSTEM_V10:START -->.*?<!-- VISUAL_SYSTEM_V10:END -->",
    re.DOTALL,
)


def parse_specs() -> tuple[VisualSpec, ...]:
    specs: list[VisualSpec] = []
    for raw_line in RAW_SPECS.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) != 10:
            raise ValueError(f"invalid visual spec: {line}")
        (
            filename,
            family,
            title,
            description,
            heading,
            subtitle,
            accent,
            icon,
            raw_stages,
            footer,
        ) = parts
        stages: list[tuple[str, str]] = []
        for raw_stage in raw_stages.split(";"):
            label, detail = raw_stage.split("~", 1)
            stages.append((label, detail))
        if len(stages) != 5:
            raise ValueError(f"visual must contain five stages: {filename}")
        if accent not in TOKENS:
            raise ValueError(f"unknown accent token: {accent}")
        specs.append(
            VisualSpec(
                filename=filename,
                family=family,
                title=title,
                description=description,
                heading=heading,
                subtitle=subtitle,
                accent=accent,
                icon=icon,
                stages=tuple(stages),
                footer=footer,
            )
        )
    if len(specs) != 42:
        raise ValueError(f"expected 42 visual specs, found {len(specs)}")
    return tuple(specs)


def wrap_words(value: str, limit: int) -> tuple[str, ...]:
    words = value.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join((*current, word))
        if current and len(candidate) > limit:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return tuple(lines[:3])


def text_lines(
    x: float,
    y: float,
    value: str,
    css_class: str,
    limit: int,
    step: int,
    *,
    anchor: str = "start",
) -> str:
    lines = wrap_words(value, limit)
    tspans = [
        f'<tspan x="{x:.1f}" dy="{0 if index == 0 else step}">{html.escape(line)}</tspan>'
        for index, line in enumerate(lines)
    ]
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{css_class}">{"".join(tspans)}</text>'


def icon_svg(kind: str, x: float, y: float, accent: str) -> str:
    common = f'color="{accent}" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "orbit":
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<ellipse rx="38" ry="14"/><ellipse rx="38" ry="14" transform="rotate(60)"/>'
            '<ellipse rx="38" ry="14" transform="rotate(-60)"/><circle r="6" fill="currentColor"/>'
            "</g>"
        )
    if kind in {"network", "molecule"}:
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<path d="M-34 20L-10-24L24-15L36 24L2 35Z"/>'
            '<circle cx="-34" cy="20" r="5"/><circle cx="-10" cy="-24" r="5"/>'
            '<circle cx="24" cy="-15" r="5"/><circle cx="36" cy="24" r="5"/>'
            '<circle cx="2" cy="35" r="5"/></g>'
        )
    if kind == "layers":
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<path d="M-38-22L0-40L38-22L0-4Z"/><path d="M-38-4L0 14L38-4"/>'
            '<path d="M-38 14L0 32L38 14"/></g>'
        )
    if kind in {"chart", "spectrum"}:
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<path d="M-42 34V-34M-42 34H44"/><path d="M-35 20L-20 4L-5 16L12-20L27-8L40-30"/>'
            '<circle cx="12" cy="-20" r="4"/></g>'
        )
    if kind == "shield":
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<path d="M0-42L34-28V0C34 22 20 36 0 44C-20 36-34 22-34 0V-28Z"/>'
            '<path d="M-14 1L-3 13L17-12"/></g>'
        )
    if kind in {"flow", "process"}:
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<rect x="-42" y="-28" width="24" height="56" rx="6"/>'
            '<rect x="18" y="-28" width="24" height="56" rx="6"/>'
            '<path d="M-18 0H18M6-12L18 0L6 12"/></g>'
        )
    if kind == "lattice":
        circles = "".join(
            f'<circle cx="{column * 24 - 24}" cy="{row * 24 - 24}" r="4"/>'
            for row in range(3)
            for column in range(3)
        )
        return f'<g transform="translate({x:.1f} {y:.1f})" {common}><path d="M-24-24H24V24H-24Z"/>{circles}</g>'
    if kind == "control":
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<path d="M-40-24H40M-40 0H40M-40 24H40"/>'
            '<circle cx="-12" cy="-24" r="7" fill="currentColor"/>'
            '<circle cx="18" cy="0" r="7" fill="currentColor"/>'
            '<circle cx="-24" cy="24" r="7" fill="currentColor"/></g>'
        )
    if kind == "hpc":
        return (
            f'<g transform="translate({x:.1f} {y:.1f})" {common}>'
            '<rect x="-40" y="-36" width="80" height="22" rx="5"/>'
            '<rect x="-40" y="-8" width="80" height="22" rx="5"/>'
            '<rect x="-40" y="20" width="80" height="22" rx="5"/>'
            '<circle cx="26" cy="-25" r="3" fill="currentColor"/>'
            '<circle cx="26" cy="3" r="3" fill="currentColor"/>'
            '<circle cx="26" cy="31" r="3" fill="currentColor"/></g>'
        )
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="36" {common}/>'


def stage_glyph(index: int, x: float, y: float, accent: str) -> str:
    if index == 0:
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="none" stroke="{accent}" stroke-width="3"/><circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{accent}"/>'
    if index == 1:
        return f'<path d="M{x - 28:.1f} {y + 16:.1f}L{x:.1f} {y - 24:.1f}L{x + 28:.1f} {y + 16:.1f}" fill="none" stroke="{accent}" stroke-width="3"/><circle cx="{x - 28:.1f}" cy="{y + 16:.1f}" r="5" fill="{accent}"/><circle cx="{x:.1f}" cy="{y - 24:.1f}" r="5" fill="{accent}"/><circle cx="{x + 28:.1f}" cy="{y + 16:.1f}" r="5" fill="{accent}"/>'
    if index == 2:
        return f'<rect x="{x - 30:.1f}" y="{y + 4:.1f}" width="12" height="24" rx="3" fill="{accent}"/><rect x="{x - 6:.1f}" y="{y - 16:.1f}" width="12" height="44" rx="3" fill="{accent}"/><rect x="{x + 18:.1f}" y="{y - 30:.1f}" width="12" height="58" rx="3" fill="{accent}"/>'
    if index == 3:
        return f'<path d="M{x:.1f} {y - 32:.1f}L{x + 32:.1f} {y:.1f}L{x:.1f} {y + 32:.1f}L{x - 32:.1f} {y:.1f}Z" fill="none" stroke="{accent}" stroke-width="3"/><path d="M{x - 14:.1f} {y:.1f}H{x + 14:.1f}" stroke="{accent}" stroke-width="3"/>'
    return f'<path d="M{x - 30:.1f} {y - 24:.1f}H{x + 30:.1f}V{y + 24:.1f}H{x - 30:.1f}Z" fill="none" stroke="{accent}" stroke-width="3"/><path d="M{x - 14:.1f} {y:.1f}L{x - 3:.1f} {y + 11:.1f}L{x + 16:.1f} {y - 12:.1f}" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'


def render_svg(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    hero = spec.filename == "hero-multiscale.svg"
    heading_size = 42 if hero else 32
    heading_x = 600.0 if hero else 56.0
    heading_anchor = "middle" if hero else "start"
    subtitle_x = heading_x
    eyebrow = "TSAO SCIENTIFIC COMPUTATION" if hero else spec.family.upper()
    card_width = 204.0
    gap = 21.0
    start_x = 48.0
    card_y = 196.0
    card_height = 270.0
    cards: list[str] = []
    arrows: list[str] = []
    for index, (label, detail) in enumerate(spec.stages):
        x = start_x + index * (card_width + gap)
        cards.extend(
            [
                f'<rect x="{x:.1f}" y="{card_y:.1f}" width="{card_width:.1f}" height="{card_height:.1f}" rx="18" class="card"/>',
                f'<rect x="{x:.1f}" y="{card_y:.1f}" width="{card_width:.1f}" height="4" rx="2" fill="{accent}"/>',
                f'<rect x="{x + 18:.1f}" y="{card_y + 20:.1f}" width="44" height="28" rx="14" fill="#0B1220" stroke="{accent}"/>',
                f'<text x="{x + 40:.1f}" y="{card_y + 39:.1f}" text-anchor="middle" class="index">{index + 1:02d}</text>',
                text_lines(x + 18, card_y + 82, label, "stage", 17, 22),
                text_lines(x + 18, card_y + 134, detail.replace(" · ", " "), "detail", 22, 22),
                stage_glyph(index, x + card_width / 2, card_y + 224, accent),
            ]
        )
        if index < 4:
            arrow_x = x + card_width + 4
            arrows.append(
                f'<path d="M{arrow_x:.1f} {card_y + 135:.1f}H{arrow_x + gap - 8:.1f}" class="arrow"/>'
            )
    evidence_labels = (
        "NUMERICAL",
        "CONVERGENCE",
        "PHYSICAL",
        "UNCERTAINTY",
        "APPLICABILITY",
        "REVIEW",
    )
    evidence: list[str] = []
    segment_width = 174.0
    for index, label in enumerate(evidence_labels):
        x = 58.0 + index * segment_width
        evidence.extend(
            [
                f'<circle cx="{x:.1f}" cy="538" r="10" fill="none" stroke="{accent}" stroke-width="2"/>',
                f'<text x="{x + 18:.1f}" y="543" class="gate">{label}</text>',
            ]
        )
    subtitle_lines = text_lines(
        subtitle_x,
        150.0 if hero else 142.0,
        spec.subtitle,
        "subtitle",
        82 if hero else 72,
        22,
        anchor="middle" if hero else "start",
    )
    footer_lines = text_lines(56.0, 620.0, spec.footer, "footer", 132, 21)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" role="img" aria-labelledby="title desc" data-design-system="{SYSTEM_ID}" data-family="{html.escape(spec.family)}">
  <title id="title">{html.escape(spec.title)}</title>
  <desc id="desc">{html.escape(spec.description)}</desc>
  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#334155" stroke-width="1" opacity="0.22"/></pattern>
  </defs>
  <style>
    .eyebrow {{ fill: {accent}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 1.8px; }}
    .heading {{ fill: {TOKENS["text"]}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: {heading_size}px; font-weight: 700; }}
    .subtitle {{ fill: {TOKENS["secondary"]}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 16px; font-weight: 400; }}
    .card {{ fill: {TOKENS["surface"]}; stroke: {TOKENS["border"]}; stroke-width: 2; }}
    .index {{ fill: {TOKENS["text"]}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: 700; }}
    .stage {{ fill: {TOKENS["text"]}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 19px; font-weight: 650; }}
    .detail {{ fill: {TOKENS["secondary"]}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 14px; font-weight: 400; }}
    .arrow {{ fill: none; stroke: {TOKENS["muted"]}; stroke-width: 2; stroke-linecap: round; }}
    .gate {{ fill: {TOKENS["secondary"]}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: 650; letter-spacing: 0.6px; }}
    .footer {{ fill: {TOKENS["muted"]}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 14px; font-weight: 400; }}
    .badge {{ fill: {TOKENS["secondary"]}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: 700; }}
  </style>
  <rect width="1200" height="680" rx="24" fill="{TOKENS["canvas"]}"/>
  <rect width="1200" height="680" rx="24" fill="url(#grid)"/>
  <rect x="32" y="28" width="1136" height="624" rx="20" fill="none" stroke="{TOKENS["border"]}" stroke-width="2"/>
  <text x="{heading_x:.1f}" y="58" text-anchor="{heading_anchor}" class="eyebrow">{html.escape(eyebrow)}</text>
  <text x="{heading_x:.1f}" y="112" text-anchor="{heading_anchor}" class="heading">{html.escape(spec.heading)}</text>
  {subtitle_lines}
  <rect x="1002" y="48" width="142" height="100" rx="16" fill="{TOKENS["raised"]}" stroke="{TOKENS["border"]}" stroke-width="2"/>
  {icon_svg(spec.icon, 1073.0, 98.0, accent)}
  <rect x="926" y="158" width="218" height="28" rx="14" fill="{TOKENS["raised"]}" stroke="{TOKENS["border"]}"/>
  <text x="1035" y="177" text-anchor="middle" class="badge">EVIDENCE-BOUND</text>
  {"".join(cards)}
  {"".join(arrows)}
  <rect x="48" y="500" width="1104" height="70" rx="16" fill="{TOKENS["raised"]}" stroke="{TOKENS["border"]}" stroke-width="2"/>
  {"".join(evidence)}
  {footer_lines}
</svg>
'''


def update_marker(text: str, block: str) -> str:
    if VISUAL_MARKER.search(text):
        return VISUAL_MARKER.sub(block, text, count=1)
    anchor = "</div>\n"
    if anchor not in text:
        raise ValueError("README center block closing tag not found")
    return text.replace(anchor, anchor + "\n" + block + "\n", 1)


def update_inventory(text: str) -> str:
    if "## UI/UX Pro Max design system" in text:
        pattern = re.compile(r"## UI/UX Pro Max design system\n.*?(?=\n## Asset set)", re.DOTALL)
        return pattern.sub(VISUAL_POLICY_BLOCK.rstrip() + "\n", text, count=1)
    return text.replace("## Asset set", VISUAL_POLICY_BLOCK + "\n## Asset set", 1)


def update_changelog(text: str) -> str:
    bullet = (
        "- Regenerated all 42 README SVG illustrations with the UI/UX Pro Max-derived "
        "Scientific Swiss Bento V10 system, preserving filenames, scientific boundaries and "
        "self-contained accessibility while removing decorative AI gradients and glow effects."
    )
    if bullet in text:
        return text
    return text.replace("## Unreleased\n", f"## Unreleased\n\n{bullet}\n", 1)


def write(path: Path, content: str, *, check: bool) -> None:
    normalized = content.rstrip() + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if check:
        if current != normalized:
            raise SystemExit(f"generated visual artifact is stale: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")


def synchronize(*, check: bool) -> None:
    specs = parse_specs()
    for spec in specs:
        write(VISUAL_ROOT / spec.filename, render_svg(spec), check=check)

    readme = ROOT / "README.md"
    readme_zh = ROOT / "README.zh-CN.md"
    inventory = VISUAL_ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    write(
        readme,
        update_marker(readme.read_text(encoding="utf-8"), README_EN_BLOCK),
        check=check,
    )
    write(
        readme_zh,
        update_marker(readme_zh.read_text(encoding="utf-8"), README_ZH_BLOCK),
        check=check,
    )
    write(
        inventory,
        update_inventory(inventory.read_text(encoding="utf-8")),
        check=check,
    )
    write(
        changelog,
        update_changelog(changelog.read_text(encoding="utf-8")),
        check=check,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the complete README visual atlas using Scientific Swiss Bento V10."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    synchronize(check=args.check)
    print("PASS: 42 UI/UX Pro Max scientific README visuals are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
