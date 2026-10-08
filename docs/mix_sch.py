import schemdraw
import schemdraw.elements as elm
schemdraw.config(fontsize=11, lw=1.2)
B = lambda **k: elm.BjtNpn(circle=True, **k).theta(0)
with schemdraw.Drawing(file='mixer_schematic.png', dpi=170, show=False) as d:
    # Q3 transconductor + Re
    q3 = d.add(B().at((6, 0)).anchor('base').label('Q3  NX=4\n(RF → current)', loc='right', ofst=(0.25, 0)))
    d.add(elm.Resistor().down().at(q3.emitter).to((6.75, -2.3)).label('Re 75 Ω', loc='bottom'))
    d.add(elm.Ground())
    # tail node
    d.add(elm.Line().at(q3.collector).to((6.75, 1.4)))
    d.add(elm.Dot().at((6.75, 1.4)))
    d.add(elm.Line().at((5.25, 1.4)).to((8.25, 1.4)))
    # switching pair
    q4 = d.add(B().at((5.25, 1.4)).anchor('emitter').label('Q4 NX=2', loc='left', ofst=(-0.1, -0.75)))
    q5 = d.add(B().reverse().at((8.25, 1.4)).anchor('emitter').label('Q5 NX=2', loc='right', ofst=(0.1, -0.75)))
    # IF nodes and loads
    d.add(elm.Line().at(q4.collector).to((5.25, 3.4)))
    d.add(elm.Dot().at((5.25, 3.4)))
    d.add(elm.Line().at(q5.collector).to((8.25, 3.4)))
    d.add(elm.Dot().at((8.25, 3.4)))
    d.add(elm.Resistor().up().at((5.25, 3.4)).to((5.25, 5.4)).label('RL\n300 Ω', loc='bottom'))
    d.add(elm.Capacitor().up().at((4.0, 3.4)).to((4.0, 5.4)).label('CL\n1.76 pF', loc='top'))
    d.add(elm.Resistor().up().at((8.25, 3.4)).to((8.25, 5.4)).label('RL\n300 Ω', loc='top'))
    d.add(elm.Capacitor().up().at((9.5, 3.4)).to((9.5, 5.4)).label('CL\n1.76 pF', loc='bottom'))
    d.add(elm.Line().at((4.0, 5.4)).to((9.5, 5.4)))
    d.add(elm.Line().up().at((6.75, 5.4)).length(0.3))
    d.add(elm.Vdd().label('VCC 2.5 V'))
    d.add(elm.Line().at((5.25, 3.4)).to((2.6, 3.4)))
    d.add(elm.Dot().at((4.0, 3.4)))
    d.add(elm.Dot(open=True).at((2.6, 3.4)).label('IF+', loc='left'))
    d.add(elm.Line().at((8.25, 3.4)).to((10.9, 3.4)))
    d.add(elm.Dot().at((9.5, 3.4)))
    d.add(elm.Dot(open=True).at((10.9, 3.4)).label('IF−', loc='right'))
    # LO inputs
    d.add(elm.Line().at(q4.base).to((2.6, 2.1)))
    d.add(elm.Dot(open=True).at((2.6, 2.1)).label('LO+', loc='left'))
    d.add(elm.Line().at(q5.base).to((10.9, 2.1)))
    d.add(elm.Dot(open=True).at((10.9, 2.1)).label('LO−', loc='right'))
    # RF input + termination/bias
    d.add(elm.Line().at(q3.base).to((5.2, 0)))
    d.add(elm.Dot().at((5.2, 0)))
    d.add(elm.Capacitor().left().at((5.2, 0)).to((3.6, 0)).label('Cdc 10 pF', loc='top'))
    d.add(elm.Dot(open=True).at((3.6, 0)).label('RF in\n(from LNA)', loc='left'))
    d.add(elm.Resistor().down().at((5.2, 0)).to((5.2, -1.8)).label('Rt 60 Ω', loc='top'))
    d.add(elm.SourceV().down().reverse().at((5.2, -1.8)).to((5.2, -3.2)).label('VB3\n1.18 V', loc='top'))
    d.add(elm.Ground())
    d.add(elm.Label().at((6.75, 7.0)).label('24 GHz single-balanced active mixer', fontsize=13))
    d.add(elm.Label().at((6.75, -4.3)).label('LO: 24.125 GHz, ≥ 0.25 V peak per side, 1.9 V DC     IF out: beat signal (kHz–MHz)', fontsize=10))
