"""
Pycrystal-based CRYSTAL output parser
"""
import io
import pkg_resources
from pycrystal import CRYSTOUT, CRYSTOUT_Error


class OutFileParser(object):

    parser_info = pkg_resources.require("pycrystal")[0].version

    def __init__(self, file):
        if not isinstance(file, (str, io.StringIO)):
            file_name = file.name
            file.close()
        else:
            file_name = file

        if not CRYSTOUT.acceptable(file_name):
            raise FileNotFoundError("{} is not a valid CRYSTAL output file".format(file_name))

        result = CRYSTOUT(file_name)
        self.info = result.info

    def get_parameters(self):
        """
         An adapter from pycrystal format to AiiDA output_parameters format, consistent with AiiDA-quantumespresso
        :param out_file: A name of file to parse
        :return: Parsed data
        """
        out_params = {
            'creator_name': "CRYSTAL",
            'creator_version': self.info["program"]
            'exchange_correlation': self.info['H'],
            'energy': self.info['energy'],
            'energy_units': 'eV',
            'energy_accuracy': abs(self.info['e_accuracy']) if self.info['e_accuracy'] else None,
            'energy_accuracy_units': 'eV',
            'converged_electronic': self.info['scf_conv'],
            'converged_ionic': self.info['ion_conv'],
            'monkhorst_pack_grid': self.info['k'],
            'number_of_atoms': self.info['n_atoms'],
            'number_of_atomic_orbitals': self.info['n_ao'],
            'number_of_electrons': self.info['n_electrons'],
            'number_of_symmetries': self.info['n_symops'],
            'parser_info': OutFileParser.parser_info,
            'parser_warnings': self.info['warns'],
            'scf_iterations': self.info['ncycles'],
            'phonons': None,
            'elastic': None,
        }
        # add phonon data from pycrystal output
        if self.info["phonons"]["ph_eigvecs"] is not None:
            out_params['phonons'] = {
                'dfp_displacements': self.info["phonons"]["dfp_disps"],
                'dfp_magnitude': self.info["phonons"]["dfp_magnitude"],
                'dielectric_tensor': self.info["phonons"]["dielectric_tensor"],
                'ir_active': self.info['phonons']['ir_active'],
                'raman_active': self.info['phonons']['raman_active'],
                'irreducible_representations': self.info['phonons']['irreps'],
                'modes_freqs': self.info["phonons"]["modes"],
                'modes_freqs_units': 'cm**(-1)',
                'eigenvectors': self.info["phonons"]["ph_eigvecs"],
                'k_degeneracy': self.info['phonons']['ph_k_degeneracy'],
                'thermodynamics': {
                    'thermal_contribution_to_vibrational_energy': self.info['phonons']['td']['et'],
                    'PV': self.info['phonons']['td']['pv'],
                    'temperature': self.info['phonons']['td']['t'],
                    'pressure': self.info['phonons']['td']['p'],
                    'TS': self.info['phonons']['td']['ts'],
                    'entropy': self.info['phonons']['td']['S'],
                    'heat_capacity': self.info['phonons']['td']['C'],
                    'temperature_units': 'K',
                    'pressure_units': 'MPa',
                    'energy_units': 'eV/cell',
                    'entropy_units': 'J/(mol*K)',
                    'heat_capacity_units': 'J/(mol*K)'
                },
                'zero_point_energy': self.info['phonons']['zpe'],
                'zero_point_energy_units': 'eV/cell'
            }
        # add elastic results to out parameters
        if self.info['elastic']['K'] is not None:
            out_params['elastic'] = {
                'elastic_constants': self.info['elastic']['elastic_constants'],
                'elastic_moduli': self.info['elastic']['elastic_moduli'],
                'elastic_constants_units': 'GPa',
                'elastic_moduli_units': 'TPa**(-1)',
                'bulk_modulus_voigt': self.info['elastic']['K_V'],
                'shear_modulus_voigt': self.info['elastic']['G_V'],
                'bulk_modulus_reuss': self.info['elastic']['K_R'],
                'shear_modulus_reuss': self.info['elastic']['G_R'],
                'bulk_modulus': self.info['elastic']['K'],
                'shear_modulus': self.info['elastic']['G'],
                'young_modulus': self.info['elastic']['E'],
                'poisson_ratio': self.info['elastic']['v'],
                'effective_moduli_units': 'GPa'
            }
        # Parameters from pycrystal parsing result as given in pwscf output-parameters
        return out_params

    def get_trajectory(self):
        return self.info['structures']
