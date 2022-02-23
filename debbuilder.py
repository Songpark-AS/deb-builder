import os, sys, re
import argparse

def bump_version(control_file, kind="patch"):
    # bump2version needs to know what the current version is.
    current_version = False
    pattern = re.compile("Version")

    for line in open(control_file, "r"):
        for match in re.finditer(pattern, line):
            current_version = line.split(":")[-1].strip()

    if current_version:
        print(f'Bumping version: {kind}')
        os.system(f'bump2version --current-version {current_version} {kind} {control_file}')

def chown_directory(directory, user='root'):
    print(f"Chowning {directory} to {user}")
    prev_owner = os.popen(f'ls -ld {directory} | awk \'{{print $3}}\'').read().strip()
    os.system(f'chown -R {user}.{user} {directory}')
    return prev_owner

def build(input_directory, output_directory):
    print("Building package")
    output_filename = os.path.basename(input_directory) + '.deb'
    os.system(f'dpkg-deb --build {input_directory} {output_directory}/{output_filename}')
    return f'{output_directory}/{output_filename}'

def upload_to_nexus(debfile, repo_url, username, password):
    print("Uploading package to nexus")
    os.system(f'curl -u "{username}:{password}" -H "Content-Type: multipart/form-data" --data-binary "@{debfile}" "{repo_url}"')

def main():
    parser = argparse.ArgumentParser(description='Deb package builder')

    # Positional arguments
    parser.add_argument('input_directory', help='Input directory of the deb package you are building')
    parser.add_argument('output_directory', nargs='?', help='Output directory of the deb package, if not provided it will output in the current directory')

    # Other optional arguments
    parser.add_argument('--bump-version', choices=['patch', 'minor', 'major'], help='Bump the version number')
    parser.add_argument('--nexus-username', help='Username for nexus, required to upload the package to nexus after build')
    parser.add_argument('--nexus-password', help='Password for nexus, required to upload the package to nexus after build')

    args = vars(parser.parse_args())

    if os.geteuid() != 0:
        print("You need root privileges to run this script")
        sys.exit(1)

    input_directory = os.path.abspath(args['input_directory'])
    output_directory = os.getcwd()
    control_file = input_directory + "/DEBIAN/control"

    if args['output_directory']:
        output_directory = args['output_directory']

    if not os.path.isfile(control_file):
        print("Debian control file does not exist, please create it.")
        sys.exit(1)

    if args['bump_version']:
        bump_version(control_file, args['bump_version'])

    prev_owner = chown_directory(input_directory)

    debfile = build(input_directory, output_directory)

    chown_directory(input_directory, prev_owner)

    if args['nexus_username'] and args['nexus_password']:
        upload_to_nexus(debfile, "https://nexus.inonit.no/repository/songpark-apt/", args['nexus_username'], args['nexus_password'])

if __name__ == "__main__":
    main()
