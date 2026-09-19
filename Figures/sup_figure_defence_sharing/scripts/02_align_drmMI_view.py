# Rotate the drmMI complex view so that Ocr has the same orientation as in the gp28 complex
# (Ocr chains superposed on CA; the rotation is applied to the camera only). Writes sessions/drmMI_aligned.pse.
# Run from the project root: PyMOL -cq scripts/02_align_drmMI_view.py
import numpy as np
from pymol import cmd
def rot(view): return np.array(view[:9]).reshape(3, 3)                    # columns = camera x,y,z axes in model coordinates
CIF_GP28 = "data/structures/ocr_panchino_gp28_gp28_data_model.cif"
CIF_DRM = "data/structures/ocr_disarm_2_disarm_2_drmmii_0_v_data_model.cif"
cmd.load("sessions/gp28_oriented.pse"); Vg = rot(cmd.get_view())     # the view you set for gp28
cmd.reinitialize(); cmd.load(CIF_DRM, "drmMI"); cmd.orient("drmMI"); vd = list(cmd.get_view())   # default view as starting point
cmd.reinitialize()
cmd.load(CIF_GP28, "gp28")
cmd.load(CIF_DRM, "drmMI")
r = cmd.align("drmMI and chain A and name CA", "gp28 and chain A and name CA", cycles=0, transform=1)
M = np.array(cmd.get_object_matrix("drmMI")).reshape(4, 4)[:3, :3]      # drmMI frame -> gp28 frame
cmd.reinitialize(); cmd.load(CIF_DRM, "drmMI")
Rn = M.T @ Vg                                                           # camera axes in drmMI coordinates
Q = rot(vd).T @ Rn
print("Ocr CA rmsd %.2f A; camera rotated by %.1f deg (in-plane %.1f deg)" %
      (r[0], np.degrees(np.arccos((np.trace(Q) - 1) / 2)), np.degrees(np.arctan2(Q[1, 0], Q[0, 0]))))
vd[:9] = Rn.flatten().tolist(); cmd.set_view(vd)
cmd.center("drmMI"); cmd.zoom("drmMI", buffer=2, complete=1)
cmd.save("sessions/drmMI_aligned.pse")
