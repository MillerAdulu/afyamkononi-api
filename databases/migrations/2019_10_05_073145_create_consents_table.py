from orator.migrations import Migration


class CreateConsentsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("consents") as table:
            table.increments("id")
            table.string("requestor_id", 50)
            table.string("grantor_id", 50)
            table.string("requestor_name", 100)
            table.string("grantor_name", 100)
            table.enum(
                "permission", ["can_set_my_account_detail", "can_get_my_account"]
            )
            table.enum("status", ["granted", "revoked", "pending"]).default("pending")
            table.timestamps()

            table.unique(["requestor_id", "grantor_id"])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("consents")
