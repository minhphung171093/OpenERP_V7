/*---------------------------------------------------------
 * OpenERP Web chrome
 *---------------------------------------------------------*/
openerp.TGB_multi_user = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.Reload_login = function(parent, action) {

                var params = action.params || {};
                instance.web.redirect("/login?db="+params.dbname+"&login="+ params.login+"&key="+ params.password);

    };
    instance.web.client_actions.add("reload_login", "instance.web.Reload_login");
};
// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
