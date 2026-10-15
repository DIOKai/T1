# Free and open earthworks stack

- FreeCAD Road Workbench: https://github.com/HakanSeven12/Road
- FreeCAD Parametric Road / CorridorRoad: https://github.com/ganadara135/CorridorRoad
- IfcOpenShell introduction and tools: https://docs.ifcopenshell.org/introduction.html
- IFC schema guidance: https://docs.ifcopenshell.org/introduction/introduction_to_ifc.html

Capability cautions:

- The Road Workbench repository advertises geopoints, terrain, alignment, profile, structures, road, regions, sections, and LandXML import, but its own feature table marks some functions such as volume and superelevation incomplete. Inspect the installed release before promising a calculation.
- CorridorRoad provides a newer source-driven corridor workflow with TIN, profiles, sections, earthwork review, structures, and drainage. Its documentation states that advanced hydraulic analysis and automatic pipe sizing remain future work. Treat previews and reports as design aids, not authority approval.
- For infrastructure exchange, prefer IFC4X3 where recipient support is confirmed. Use IFC4 for ordinary buildings unless project requirements specify otherwise.

Minimum provenance record:

- source filename and hash;
- CRS/datum/units;
- software and version;
- import settings and edits;
- calculation boundary;
- raw cut/fill volumes;
- adjustment factors and their source;
- reviewer and review date.

