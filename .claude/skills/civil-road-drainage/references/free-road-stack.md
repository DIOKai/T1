# Free road, drainage, and IFC references

- FreeCAD Road Workbench: https://github.com/HakanSeven12/Road
- FreeCAD Parametric Road / CorridorRoad: https://github.com/ganadara135/CorridorRoad
- IFC4X3 guidance for infrastructure: https://docs.ifcopenshell.org/introduction/introduction_to_ifc.html
- buildingSMART `IfcAlignment`: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcAlignment.htm
- IfcOpenShell alignment API: https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/alignment/index.html

Key constraints:

- IFC4X3 is the appropriate IFC generation for roads, railways, bridges, and other linear infrastructure when the receiving software supports it.
- `IfcAlignment` represents the reference system and geometry for linear infrastructure.
- The IfcOpenShell alignment API creates and maintains semantic and geometric alignment definitions, but explicitly does not select design-rule parameters such as minimum curve radius from speed or sight distance. Those values must come from the governing standard and engineer.
- CorridorRoad documents geometry, earthwork, structures, and drainage workflows, but advanced hydraulic analysis and automatic pipe sizing are not a substitute for a verified hydraulic model.

Never silently downgrade IFC4X3 linear infrastructure to IFC4/IFC2X3. Document what alignment semantics or geometry may be lost.
