// Fire physics reference. Add an `href` to any entry to turn its source label into a link.
const CONTROL = [
  ["Fuel", "Fuel material, Fuel form, Fuel geometry"],
  ["Atmosphere", "Oxygen concentration, Diluent gas, Pressure, Ambient temperature"],
  ["Flow", "Flow regime, Flow velocity, Gravity level"],
  ["Flame", "Ignition source, Flame geometry, Flame spread rate, Peak temperature, Extinction mode, Limiting oxygen"],
  ["Products", "Combustion products"],
];

const FACTS = [
  ["Buoyancy and flame shape.", "On Earth, hot gas rises and draws fresh air in, stretching the flame upward. With no buoyant flow in microgravity, flames take spherical or dome shapes.", "How Fire Burns in Space (ZME Science)"],
  ["Oxygen transport.", "Without buoyancy, oxygen reaches the flame by diffusion or by an imposed flow. Combustion gases such as CO2 can linger and limit inward oxygen diffusion, which can extinguish a flame soon after ignition.", "How Fire Burns in Space (ZME Science)"],
  ["Low-speed flow.", "In normal gravity a flame induces buoyant flow of roughly 30 cm/s or more, so spread at lower flow speeds cannot be tested. In microgravity it can.", "JAXA FLARE investigation"],
  ["Flammability limits.", "Tests report that materials can burn at lower oxygen concentrations in microgravity than in normal gravity.", "BASS-II flammability limits (Texas Tech repository)"],
  ["Near-limit flames.", "As oxygen is reduced, flames can shrink to small spherical or circular flames, or break into flamelets, and may oscillate before extinction.", "BASS-II (Texas Tech) and IIT Madras"],
  ["Heat transfer.", "In microgravity radiation becomes the dominant heat-transfer mode and gas residence times are longer.", "IIT Madras seminar abstract"],
  ["Extinction and spread.", "NASA combustion research has distinguished diffusive from radiative extinction and found sub-buoyant flows matter for flame spread.", "NASA combustionLAB RFI (SpaceRef)"],
  ["Cool flames.", "Analysis of FLEX data showed some fuel droplets can burn for a long time without a visible flame.", "NASA PSI Users Group"],
  ["Ventilation and atmosphere.", "In ISS-condition tests flames quenched when ventilation stopped, but at high oxygen and low pressure flames may survive without flow, so ISS findings may not transfer to exploration atmospheres.", "BASS-II (Texas Tech repository)"],
  ["Partial gravity.", "Drop-tower data indicate flammability limits are lower in low and partial gravity. More research is needed for lunar and Mars gravity.", "NASA NTRS: Large Scale Experiments on Spacecraft Fire Safety"],
];

const Src = ({ href, children }) =>
  href ? <a href={href} target="_blank" rel="noreferrer">{children}</a> : <span className="src">{children}</span>;

export default function Reference() {
  return (
    <div className="ref">
      <h3>Controlling variables</h3>
      {CONTROL.map(([k, v]) => <p key={k}><b>{k}:</b> {v}</p>)}
      <h3>Microgravity vs Earth</h3>
      {FACTS.map(([k, v, s, href]) => <p key={k}><b>{k}</b> {v} <Src href={href}>{s}</Src></p>)}
    </div>
  );
}
