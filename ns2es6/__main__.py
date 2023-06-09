import os, sys, argparse, logging, json
from ns2es6.transforms import (sanitize,
                               collect_exports,
                               replace_imports,
                               fully_qualify,
                               replace_qualified_with_import)
from ns2es6.utils.logger import logger

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("--debug", "-v", action="store_true")
  parser.add_argument("--clean", action="store_true")
  return parser.parse_args()

def set_logger_level(args):
  if args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

def clean():
  os.system("git clean -fd")
  os.system("git reset --hard start")

def program(args):
  os.chdir(args.directory)
  if args.clean:
    clean()
  apply_pre_patches()
  exports = collect_exports.run(args.directory)
  replace_imports.run(args.directory)
  fully_qualify.run(args.directory, exports)
  #open("/tmp/addresses.json", "w").write(json.dumps([str(x) for x in exports]))
  replace_qualified_with_import.run(args.directory, exports)
  sanitize.run(args.directory, True)
  add_globals(args.directory)

def apply_pre_patches():
  # TODO Eventually need to auto-set a "git tag" (and remove on clean())
  for root, _, files in os.walk("/Users/alanhape/Projects/ns2es6/pre"):
    for patch_file in sorted(files):
      full_path = os.path.join(root, patch_file)
      logger.info("Applying patch %s", patch_file)
      os.system(f"git apply --whitespace=fix {full_path}")
      os.system(f'git commit --quiet -am "{patch_file}"')

def add_globals(directory):
  with open(os.path.join(directory, "ts", "global.d.ts"), "w", encoding="utf8") as f:
    f.write(r"""
import { IPageDefinition } from "Brightmetrics/Interfaces/ipagedefinition";
import { IBrightCompany } from "Brightmetrics/Interfaces/ibrightcompany";
import { IBrightUser } from "Brightmetrics/Interfaces/ibrightuser";
import { IAppInfo } from "Brightmetrics/Interfaces/iappinfo";
import { IDataSourceGroup } from "Brightmetrics/Interfaces/idatasourcegroup";
import { IDataConnectionGroupTeir } from "Brightmetrics/DataSources/Interfaces/idataconnectiongroupteir";
import { IDashboardTab } from "Brightmetrics/Interfaces/idashboardtab";
import { IBrightPermission } from "Brightmetrics/Interfaces/ibrightpermission";
import { INotice } from "Brightmetrics/Interfaces/inotice";
import { DataHostRegion } from "Brightmetrics/Enums/datahostregion";
declare global {
  declare const _: _.UnderscoreStatic;
  declare const Brightmetrics: any;
  declare const sidebarPages: IPageDefinition[];
  declare const companyInfo: {
      success: boolean;
      logofile?: string;
      company: IBrightCompany;
  };
  declare const userInfo: IBrightUser;
  declare const appInfo: IAppInfo;
  declare const dataConnectionGroups: IDataSourceGroup[];
  declare const defCompanyId: number;
  declare const myUserId: number;
  declare const minWaitTime: number;
  declare const sessionToken: string | undefined;
  declare const isPublicDashboardPage: boolean | undefined;
  declare const supportedTimeZones: Array<{ id: string, label: string }>;
  declare const windowsZones: {
      supportedTimeZones: Array<{ id: string, label: string }>,
      tzmapping: Array<[string, Array<[string, string, boolean]>]>
  };
  declare const dashboardTabs: IDashboardTab[] | undefined;
  declare const whiteLabelProductName: string;
  declare const currentDataHostRegion: DataHostRegion;
  declare const router: IRouter;
  declare const roleInfo: { role: { Permissions: IBrightPermission[] } };
  declare const safeSessionStorage: Storage;
  declare const dataDefinitionTooltips: Record<string, string>;
  declare let userMessages: INotice[];
  declare let companyNotices: INotice[];
  declare const teirLevelInfo: IDataConnectionGroupTeir[];
  declare const brightmetricsStorageUrl: string | undefined;
  declare const bugsnagClient: {
      notify: (err: any, opts: {
          beforeSend?: (report: any) => void;
          metaData?: Record<string, any>;
          severity?: string;
      }) => void
  };
  declare const featureTreatments: {
      user: { [featureName: string]: string },
      company: { [featureName: string]: string }
  };
  declare const releaseStage: "production" |
                              "beta" |
                              "testing" |
                              "development";
}
    """.strip())

def undo_git_changes():
  clean()

def main():
  args = parse_args()
  set_logger_level(args)
  try:
    program(args)
  except:
    undo_git_changes()
    raise

if __name__ == "__main__":
  main()
