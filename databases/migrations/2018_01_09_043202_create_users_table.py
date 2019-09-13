from orator.migrations import Migration


class CreateUsersTable(Migration):

    def up(self):
        """Run the migrations."""
        with self.schema.create('users') as table:
            table.increments('id')
            table.string('name').unique()
            table.string('email').unique()
            table.string('password')
            table.string('private_key')
            table.string('public_key')
            table.string('type')
            table.timestamp('verified_at').nullable()
            table.timestamps()

    def down(self):
        """Revert the migrations."""
        self.schema.drop('users')
