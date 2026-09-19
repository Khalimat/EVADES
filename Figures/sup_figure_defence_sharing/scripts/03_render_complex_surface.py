# Panel B: each complex as a transparent surface over a cartoon, in the view saved in the oriented sessions.
# Colours, 0.6 transparency and lighting as in Figure 1 panel C: defence protein violet, Ocr grey70.
# chain A = Ocr, chain B = defence protein.   Run from the project root: PyMOL -cq scripts/03_render_complex_surface.py   (COMPLEXES="gp28" to render one)
import os
from pymol import cmd
SESSIONS = {"drmMI": "sessions/drmMI_aligned.pse", "gp28": "sessions/gp28_oriented.pse"}   # sessions holding the view you set
VIOLET, GREY70, TRANSP = [0.72, 0.53, 0.87], [0.7, 0.7, 0.7], 0.6
for name in os.environ.get("COMPLEXES", "drmMI gp28").split():
    cmd.reinitialize(); cmd.load(SESSIONS[name]); obj = cmd.get_names("objects")[0]
    view = cmd.get_view()
    cmd.bg_color("white")
    for k, v in [("ray_shadows", 1), ("specular", 0.15), ("antialias", 2), ("depth_cue", 0), ("orthoscopic", 1),
                 ("surface_quality", 1), ("cartoon_fancy_helices", 1), ("cartoon_loop_radius", 0.2)]:
        cmd.set(k, v)
    cmd.set_color("cas_violet", VIOLET); cmd.set_color("partner_grey", GREY70)
    cmd.hide("everything"); cmd.show("cartoon", obj); cmd.show("surface", obj)
    cmd.color("cas_violet", obj + " and chain B"); cmd.color("partner_grey", obj + " and chain A")
    cmd.set("transparency", TRANSP, obj)
    cmd.set_view(view)
    cmd.png("panels/panelB_%s_complex.png" % name, 1800, 1500, dpi=300, ray=1)
