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
  declare const Highcharts: Highcharts.Static;
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
