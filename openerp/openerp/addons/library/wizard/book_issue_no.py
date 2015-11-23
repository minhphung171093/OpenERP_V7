from openerp.osv import osv,fields

class book_name(osv.TransientModel):
    
    _name="book.name"
    _description="Book Name"
    _columns={
                'name': fields.many2one('product.product', 'Book Name', required=True),
                'card_id': fields.many2one("library.card", "Card No", required=True), 
              }
    
    def create_new_books(self, cr, uid, ids,vals, context=None):
        if context is None:
            context = {}
        lib_book_obj = self.pool.get('library.book.issue')
        for rec in self.browse(cr,uid,ids,context=context):
            lib_book_obj.create(cr, uid, {'name':rec.name.id, 'card_id':rec.card_id.id},context=context)
        
        return {}
   
book_name()