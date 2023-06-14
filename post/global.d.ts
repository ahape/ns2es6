import { IPageDefinition } from "./Interfaces/ipagedefinition";
import { IBrightCompany } from "./Interfaces/ibrightcompany";
import { IBrightUser } from "./Interfaces/ibrightuser";
import { IAppInfo } from "./Interfaces/iappinfo";
import { IDataSourceGroup } from "./Interfaces/idatasourcegroup";
import { IDataConnectionGroupTeir } from "./DataSources/Interfaces/idataconnectiongroupteir";
import { IDashboardTab } from "./Dashboard/Interfaces/idashboardtab";
import { IBrightPermission } from "./Interfaces/ibrightpermission";
import { INotice } from "./Interfaces/inotice";
import { DataHostRegion } from "./Enums/datahostregion";
declare global {
    const _: _.UnderscoreStatic;
    const Highcharts: Highcharts.Static;
    const Brightmetrics: any;
    const sidebarPages: IPageDefinition[];
    const companyInfo: {
        success: boolean;
        logofile?: string;
        company: IBrightCompany;
    };
    const userInfo: IBrightUser;
    const appInfo: IAppInfo;
    const dataConnectionGroups: IDataSourceGroup[];
    const defCompanyId: number;
    const myUserId: number;
    const minWaitTime: number;
    const sessionToken: string | undefined;
    const isPublicDashboardPage: boolean | undefined;
    const supportedTimeZones: Array<{ id: string, label: string }>;
    const windowsZones: {
        supportedTimeZones: Array<{ id: string, label: string }>,
        tzmapping: Array<[string, Array<[string, string, boolean]>]>
    };
    const dashboardTabs: IDashboardTab[] | undefined;
    const whiteLabelProductName: string;
    const currentDataHostRegion: DataHostRegion;
    const router: IRouter;
    const roleInfo: { role: { Permissions: IBrightPermission[] } };
    const safeSessionStorage: Storage;
    const dataDefinitionTooltips: Record<string, string>;
    let userMessages: INotice[];
    let companyNotices: INotice[];
    const teirLevelInfo: IDataConnectionGroupTeir[];
    const brightmetricsStorageUrl: string | undefined;
    const bugsnagClient: {
        notify: (err: any, opts: {
            beforeSend?: (report: any) => void;
            metaData?: Record<string, any>;
            severity?: string;
        }) => void
    };
    const featureTreatments: {
        user: { [featureName: string]: string },
        company: { [featureName: string]: string }
    };
    const releaseStage: "production" |
                        "beta" |
                        "testing" |
                        "development";
}
