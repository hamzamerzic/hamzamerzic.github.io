#!/usr/bin/env python3
import os
import argparse
import subprocess
import numpy as np
import pymeshlab


def fmt(x):
    return "{: .10e}".format(x)


def clean_mesh(
    input_file,
    mass,
    output_dir="/tmp/results",
    save_normals=False,
    use_convex_hull=False,
    verbose=False,
):
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"File '{input_file}' not found.")

    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(input_file))[0]
    stl_file = os.path.join(output_dir, f"{basename}.stl")
    dae_file = os.path.join(output_dir, f"{basename}.dae")

    original_size = os.path.getsize(input_file)

    if verbose:
        print(f"[INFO] Converting input to .stl and .dae via assimp")
    subprocess.run(["assimp", "export", input_file, stl_file], check=True)
    subprocess.run(["assimp", "export", stl_file, dae_file], check=True)

    if verbose:
        print(f"[INFO] Loading mesh: {dae_file}")
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(dae_file)

    if verbose:
        print(f"[INFO] Initial face count: {ms.current_mesh().face_number()}")
        print(f"[INFO] Initial vertex count: {ms.current_mesh().vertex_number()}")

    # === Apply cleaning filters ===
    ms.apply_filter("meshing_remove_duplicate_faces")
    ms.apply_filter("meshing_remove_duplicate_vertices")
    ms.apply_filter("meshing_repair_non_manifold_edges")
    ms.apply_filter("compute_normal_per_face")
    ms.apply_filter("compute_normal_per_vertex")
    ms.apply_filter(
        "compute_matrix_from_scaling_or_normalization", axisx=100.0, uniformflag=True
    )
    ms.apply_filter("apply_matrix_freeze")

    if use_convex_hull:
        ms.generate_convex_hull()
        geo = ms.get_geometric_measures()

    geo = ms.get_geometric_measures()

    if "inertia_tensor" not in geo:
        if verbose:
            print("[INFO] Mesh not watertight — generating convex hull")
        cleaned_size = os.path.getsize(dae_file)
        return (
            f"Mesh is not 'watertight'.\n"
            f"Original size: {original_size / 1024:.2f} KB\n"
            f"Cleaned size: {cleaned_size / 1024:.2f} KB\n",
            dae_file,
        )

    # Save mesh to file
    # Vertex normals are used for lighting/shading in rendering engines (e.g., Gazebo, Blender, etc.).
    # Disable them if the output is used purely for physics/simulation and file size matters.
    ms.save_current_mesh(
        dae_file,
        save_vertex_color=True,
        save_vertex_coord=True,
        save_vertex_normal=save_normals,
        save_wedge_texcoord=False,
        save_wedge_normal=False,
    )

    cleaned_size = os.path.getsize(dae_file)

    if verbose:
        print(f"[INFO] Cleaned face count: {ms.current_mesh().face_number()}")
        print(f"[INFO] Cleaned vertex count: {ms.current_mesh().vertex_number()}")
        print(f"[INFO] Original size: {original_size / 1024:.2f} KB")
        print(f"[INFO] Cleaned size:  {cleaned_size / 1024:.2f} KB")

    volume = geo["mesh_volume"]
    com = np.array(geo["center_of_mass"])
    inertia = np.array(geo["inertia_tensor"])
    norm_volume = volume / 1e6
    norm_com = com / 1e2
    inertia = inertia / volume / 1e4 * mass

    xml = (
        "<inertial>\n"
        f"  <!-- Volume: {fmt(norm_volume)} -->\n"
        f"  <mass> {mass} </mass>\n\n"
        f"  <!-- Center of mass: {' '.join(map(fmt, norm_com))} -->\n"
        f"  <pose> {' '.join(map(fmt, norm_com))} 0 0 0 </pose>\n\n"
        "  <!-- Inertia matrix -->\n"
        "  <inertia>\n"
        f"    <ixx> {fmt(inertia[0][0])} </ixx>\n"
        f"    <ixy> {fmt(inertia[0][1])} </ixy>\n"
        f"    <ixz> {fmt(inertia[0][2])} </ixz>\n"
        f"    <iyy> {fmt(inertia[1][1])} </iyy>\n"
        f"    <iyz> {fmt(inertia[1][2])} </iyz>\n"
        f"    <izz> {fmt(inertia[2][2])} </izz>\n"
        "  </inertia>\n"
        "</inertial>\n"
        f"\nOriginal size: {original_size / 1024:.2f} KB\n"
        f"Cleaned size: {cleaned_size / 1024:.2f} KB\n"
    )

    return xml, dae_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and analyze a 3D mesh file.")
    parser.add_argument("input_file", help="Path to input mesh file (e.g., STL, OBJ)")
    parser.add_argument("mass", type=float, help="Mass of the object in kg")
    parser.add_argument(
        "--save-normals", action="store_true", help="Save vertex normals in DAE output."
    )
    parser.add_argument(
        "--use-convex-hull",
        action="store_true",
        help="Generate convex hull.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print debug output.")

    args = parser.parse_args()

    xml, output_path = clean_mesh(
        args.input_file,
        args.mass,
        save_normals=args.save_normals,
        use_convex_hull=args.use_convex_hull,
        verbose=args.verbose,
    )

    print("\n=== Output XML ===\n")
    print(xml)
    print(f"\nCleaned mesh saved at: {output_path}")
