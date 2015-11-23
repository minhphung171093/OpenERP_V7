


from openerp.osv import osv,fields

class update_books(osv.TransientModel):
    
    _name="update.books"
    _description="Update Books"
    _columns={
               'name': fields.many2one('product.product', 'Book Name', required=True), 
              }
    
    def action_update_books(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        lib_book_obj = self.pool.get('library.book.issue')
        for rec in self.browse(cr,uid,ids,context=context):
            active_ids= context.get('active_ids',False)
            if active_ids:
                lib_book_obj.write(cr,uid,active_ids,{'name':rec.name.id},context=context)

        return {}
    
update_books()