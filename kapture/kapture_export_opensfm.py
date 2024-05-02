
import argparse
import logging
import os.path as path
import path_to_kapture  # enables import kapture  # noqa: F401
import kapture
import kapture.utils.logging
from kapture.io.records import TransferAction
from kapture.converter.opensfm.export_opensfm import export_opensfm


logger = logging.getLogger('opensfm')


def export_opensfm_command_line():
    """
    Exports openSfM from kapture.
    """
    parser = argparse.ArgumentParser(description='Exports from kapture to openSfM')
    parser_verbosity = parser.add_mutually_exclusive_group()
    parser_verbosity.add_argument(
        '-v', '--verbose', nargs='?', default=logging.WARNING, const=logging.INFO,
        action=kapture.utils.logging.VerbosityParser,
        help='verbosity level (debug, info, warning, critical, ... or int value) [warning]')
    parser_verbosity.add_argument(
        '-q', '--silent', '--quiet', action='store_const', dest='verbose', const=logging.CRITICAL)
    ####################################################################################################################
    parser.add_argument('-k', '--kapture', required=True,
                        help='path to kapture root directory.')
    parser.add_argument('-o', '--opensfm', required=True,
                        help='directory where to save OpenSfM files.')
    parser.add_argument('--transfer', type=TransferAction, default=TransferAction.link_absolute,
                        help=f'How to export images [link_absolute], choose among: '
                             f'{", ".join(a.name for a in TransferAction)}')
    parser.add_argument('-f', '-y', '--force', action='store_true', default=False,
                        help='Force delete opensfm data if already exists.')
    parser.add_argument('-kpt', '--keypoints-type', default=None, help='kapture keypoints type.')
    parser.add_argument('-desc', '--descriptors-type', default=None, help='kapture descriptors type.')
    args = parser.parse_args()
    ####################################################################################################################
    logger.setLevel(args.verbose)
    if args.verbose <= logging.DEBUG:
        # for debug, let kapture express itself.
        kapture.utils.logging.getLogger().setLevel(args.verbose)

    logger.debug('\\\n'.join(
        '--{:20} {:100}'.format(k, str(v))
        for k, v in vars(args).items()
        if k != 'command'))

    args.kapture = path.normpath(path.abspath(args.kapture))
    args.opensfm = path.normpath(path.abspath(args.opensfm))
    export_opensfm(args.kapture, args.opensfm, args.force, args.transfer, args.keypoints_type, args.descriptors_type)


if __name__ == '__main__':
    export_opensfm_command_line()
