from orator.migrations import Migration


class CreateUsersTable(Migration):
    def up(self):
        """Run the migrations."""
        with self.schema.create("users") as table:
            table.increments("id")
            table.string("gov_id").unique()
            table.string("name")
            table.string("email").unique().nullable()
            table.string("phone_number").unique().nullable()
            table.string("password")
            table.string("private_key")
            table.string("public_key")
            table.string("type")
            table.string("remember_token").nullable()
            table.timestamp("verified_at").nullable()
            table.timestamps()

    def down(self):
        """Revert the migrations."""
        self.schema.drop("users")
