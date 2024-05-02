
import argparse
import logging
import os.path as path
import path_to_kapture  # enables import kapture  # noqa: F401
import kapture
from kapture.io.records import TransferAction
from kapture.converter.opensfm.import_opensfm import import_opensfm


logger = logging.getLogger('opensfm')


def import_opensfm_command_line():
    """
    Imports openSfM to kapture.
    """
    parser = argparse.ArgumentParser(description='Imports openSfM to kapture')
    parser_verbosity = parser.add_mutually_exclusive_group()
    parser_verbosity.add_argument(
        '-v', '--verbose', nargs='?', default=logging.WARNING, const=logging.INFO,
        action=kapture.utils.logging.VerbosityParser,
        help='verbosity level (debug, info, warning, critical, ... or int value) [warning]')
    parser_verbosity.add_argument(
        '-q', '--silent', '--quiet', action='store_const', dest='verbose', const=logging.CRITICAL)
    ####################################################################################################################
    parser.add_argument('-i', '--input', '--opensfm', required=True,
                        help='path to OpenSfM root directory.')
    parser.add_argument('-o', '-k', '--output', '--kapture', required=True,
                        help='output directory where to save kapture files.')
    parser.add_argument('--transfer', type=TransferAction, default=TransferAction.link_absolute,
                        help=f'How to import images [link_absolute], choose among: '
                             f'{", ".join(a.name for a in TransferAction)}')
    parser.add_argument('-f', '-y', '--force', action='store_true', default=False,
                        help='Force delete kapture if already exists.')
    parser.add_argument('--keypoints-type', default='HessianAffine', help='kapture keypoints type.')
    parser.add_argument('--descriptors-type', default='HOG', help='kapture descriptors type.')
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

    args.input = path.normpath(path.abspath(args.input))
    args.output = path.normpath(path.abspath(args.output))

    import_opensfm(args.input, args.output, args.force, args.transfer, args.keypoints_type, args.descriptors_type)


if __name__ == '__main__':
    import_opensfm_command_line()
