"""
module to write CRYSTAL17 .d12 files
"""
from aiida_crystal.utils import get_keys
from aiida_crystal.validation import validate_with_json


def format_value(dct, keys):
    """return the value + a new line, or empty string if keys not found"""
    value = get_keys(dct, keys, None)
    if value is None:
        return ""
    if isinstance(value, dict):
        outstr = ""
        for keyword in value.keys():
            args = value[keyword]
            if isinstance(args, bool):
                if args:
                    outstr += "{}\n".format(keyword)
            elif isinstance(args, (list, tuple)):
                outstr += "{0}\n{1}\n".format(keyword,
                                              " ".join([str(a) for a in args]))
            else:
                outstr += "{0}\n{1}\n".format(keyword, args)
        return outstr

    return "{}\n".format(value)


def write_input(indict, basis, atom_props=None):
    """write input of a validated input dictionary

    :param indict: dictionary of input
    :param basis: a basis family or a list of basis sets
    :param atom_props: dictionary of atom ids with specific properties ("spin_alpha", "spin_beta", "unfixed", "ghosts")
    :return:
    """
    from aiida_crystal.data.basis_family import CrystalBasisFamilyData
    is_basis_family = isinstance(basis, CrystalBasisFamilyData)
    # validation
    validate_with_json(indict)
    if not basis:
        raise ValueError("there must be a basis family or a list of basis sets present")
    elif not (is_basis_family or
              (isinstance(basis, list) and all([hasattr(b, "content") for b in basis]))):
        raise ValueError("basis must be a family or a list of basis sets")

    if atom_props is None:
        atom_props = {}
    if not set(atom_props.keys()).issubset(
            ["spin_alpha", "spin_beta", "unfixed", "ghosts"]):
        raise ValueError(
            "atom_props should only contain: 'spin_alpha', 'spin_beta', 'unfixed', 'ghosts'"
        )
    # validate that a index isn't in both spin_alpha and spin_beta
    allspin = atom_props.get("spin_alpha", []) + atom_props.get(
        "spin_beta", [])
    if len(set(allspin)) != len(allspin):
        raise ValueError(
            "a kind cannot be in both spin_alpha and spin_beta: {}".format(
                allspin))

    outstr = ""

    # Title
    title = get_keys(indict, ["title"], "CRYSTAL run")
    outstr += "{}\n".format(" ".join(title.splitlines()))  # must be one line

    outstr = _geometry_block(outstr, indict, atom_props)

    outstr = _basis_set_block(outstr, indict, basis, atom_props, is_basis_family)

    outstr = _hamiltonian_block(outstr, indict, atom_props)

    return outstr


def _hamiltonian_block(outstr, indict, atom_props):
    # Hamiltonian Optional Keywords
    outstr += format_value(indict, ["scf", "single"])
    # DFT Optional Block
    if get_keys(indict, ["scf", "dft"], False):

        outstr += "DFT\n"

        xc = get_keys(indict, ["scf", "dft", "xc"], raise_error=True)
        if isinstance(xc, (tuple, list)):
            if len(xc) == 2:
                outstr += "CORRELAT\n"
                outstr += "{}\n".format(xc[0])
                outstr += "EXCHANGE\n"
                outstr += "{}\n".format(xc[1])
        else:
            outstr += format_value(indict, ["scf", "dft", "xc"])

        if get_keys(indict, ["scf", "dft", "SPIN"], False):
            outstr += "SPIN\n"

        outstr += format_value(indict, ["scf", "dft", "grid"])
        outstr += format_value(indict, ["scf", "dft", "grid_weights"])
        outstr += format_value(indict, ["scf", "dft", "numerical"])

        outstr += "END\n"

    # # K-POINTS (SHRINK\nPMN Gilat)
    outstr += "SHRINK\n"
    outstr += "{0} {1}\n".format(
        *get_keys(indict, ["scf", "k_points"], raise_error=True))
    # ATOMSPIN
    spins = []
    for anum in atom_props.get("spin_alpha", []):
        spins.append((anum, 1))
    for anum in atom_props.get("spin_beta", []):
        spins.append((anum, -1))
    if spins:
        outstr += "ATOMSPIN\n"
        outstr += "{}\n".format(len(spins))
        for anum, spin in sorted(spins):
            outstr += "{0} {1}\n".format(anum, spin)

    # SCF/Other Optional Keywords
    outstr += format_value(indict, ["scf", "numerical"])
    outstr += format_value(indict, ["scf", "fock_mixing"])
    outstr += format_value(indict, ["scf", "spinlock"])
    for keyword in get_keys(indict, ["scf", "post_scf"], []):
        outstr += "{}\n".format(keyword)

    # Hamiltonian and SCF End
    outstr += "END\n"
    return outstr


def _geometry_block(outstr, indict, atom_props):
    # Geometry
    outstr += "EXTERNAL\n"  # we assume external geometry
    # Geometry Optional Keywords (including optimisation)
    for keyword in get_keys(indict, ["geometry", "info_print"], []):
        outstr += "{}\n".format(keyword)
    for keyword in get_keys(indict, ["geometry", "info_external"], []):
        outstr += "{}\n".format(keyword)
    if "optimise" in indict.get("geometry", {}):
        outstr += "OPTGEOM\n"
        outstr += format_value(indict, ["geometry", "optimise", "type"])
        unfixed = atom_props.get("unfixed", [])
        if unfixed:
            outstr += "FRAGMENT\n"
            outstr += "{}\n".format(len(unfixed))
            outstr += " ".join([str(a) for a in sorted(unfixed)]) + " \n"
        outstr += format_value(indict, ["geometry", "optimise", "hessian"])
        outstr += format_value(indict, ["geometry", "optimise", "gradient"])
        for keyword in get_keys(indict, ["geometry", "optimise", "info_print"],
                                []):
            outstr += "{}\n".format(keyword)
        outstr += format_value(indict, ["geometry", "optimise", "convergence"])
        outstr += "ENDOPT\n"
    if "phonons" in indict.get("geometry", {}):
        freq_dict = indict["geometry"]["phonons"]
        outstr += "FREQCALC\n"
        outstr += "TEMPERAT\n"
        outstr += "%s %s %s\n" % (35, 5.7125, 1000)
        for keyword in freq_dict.get("info_print", []):
            outstr += "{}\n".format(keyword)
        if "ir" in freq_dict and freq_dict["ir"]:
            outstr += "INTENS\n"
            outstr += format_value(freq_dict, ["ir", "technique"])
        if "raman" in freq_dict and freq_dict["raman"]:
            outstr += "INTRAMAN\n"
            outstr += "INTCPHF\n"
            outstr += "END\n"
        outstr += "ENDFREQ\n"
    if "elastic_constants" in indict.get("geometry", {}):
        ela_dict = indict["geometry"]["elastic_constants"]
        outstr += '{}\n'.format(ela_dict['type'])
        outstr += format_value(indict, ["geometry", "elastic_constants", "convergence"])
        outstr += 'END\n'
    # somehow it seems that if basis set is given by keyword the geometry block must not end with END
    # thus ENDGEOM found its place in basis set block
    return outstr


def _basis_set_block(outstr, indict, basis, atom_props, is_basis_family):
    # Basis Sets
    if is_basis_family:
        content = basis.content
        if "BASISSET" not in content:
            # not predefined basis family, so geometry should end with END
            outstr += "END\n"
        outstr += content
        # basis sets end
        if "BASISSET" not in content:
            outstr += "END\n"
    elif isinstance(basis, list):
        # Geometry End
        outstr += "END\n"
        outstr += '\n'.join([b.content for b in basis])
        outstr += '\n99 0\n'
        # GHOSTS
        ghosts = atom_props.get("ghosts", [])
        if ghosts:
            outstr += "GHOSTS\n"
            outstr += "{}\n".format(len(ghosts))
            outstr += " ".join([str(a) for a in sorted(ghosts)]) + " \n"
            # GHOSTS and CHEMOD need its own END
        outstr += "END\n"

    # Basis Sets Optional Keywords
    outstr += format_value(indict, ["basis_set"])
    return outstr
