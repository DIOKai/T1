# FreeCAD FEM and CalculiX reference

Primary references:

- FreeCAD FEM tutorial: https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/FEM_tutorial.html
- FreeCAD CalculiX integration: https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/FEM_CalculiX.html
- FreeCAD FEM preferences: https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/FEM_Preferences.html
- FreeCAD CalculiX solver control: https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/FEM_SolverCalculixCcxtools.html
- FreeCAD FEM scripted tutorial: https://reqrefusion.github.io/FreeCAD-Documentation-html/wiki/FEM_Tutorial_Python.html

Verified technical points:

- CalculiX is FreeCAD FEM's default structural/thermo-mechanical solver and is GPL-licensed.
- FreeCAD communicates with CalculiX through text input/output files.
- The CalculiX input deck written by FreeCAD uses the SI(mm) system: mm, N, tonne, s, MPa, mJ, tonne/mm³, and K. CalculiX itself does not enforce units, so mixed inputs can produce plausible-looking but wrong results.
- Supported analysis modes include linear/nonlinear static, frequency, linear buckling, and thermal/thermo-mechanical workflows, subject to the installed FreeCAD/solver version.
- Supported elements and result objects differ by solver implementation and FreeCAD version. Inspect the installed version rather than relying on an old tutorial.

Minimum review record:

- FreeCAD, mesher, and CalculiX versions;
- geometry idealization and element types;
- material/section sources;
- restraints, releases, contacts, and loads;
- mesh statistics and quality checks;
- solver warnings;
- reaction balance;
- mesh-sensitivity comparison;
- hand/benchmark comparison;
- limitations and engineer sign-off status.
