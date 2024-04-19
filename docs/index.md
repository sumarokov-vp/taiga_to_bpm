# Welcome to bot documentation

## Bot commands

* `/myid` - Get my telegram id for adding to bot_users table.
* `/reports` - Show reports menu.
* `/commands` - Show commands menu.

## Reports

Reports list based on database table `bot_reports`. To add new report you need to add new record to this table. Report will be shown as table in bot. Use `report_query` field to set sql query for generating report.
After adding new report you need to add permissions for this report in `bot_roles_report` table.
