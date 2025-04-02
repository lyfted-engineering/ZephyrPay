import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select

from backend.app.models.user import User
from backend.app.services.role import get_user_role, update_user_role, assign_initial_role
from backend.app.schemas.role import RoleEnum, RoleUpdate, RoleRead
from backend.app.core.errors import NotFoundError, PermissionError


def test_role_schema_init():
    """Test initialization of role schemas"""
    # Test RoleRead schema
    role_read = RoleRead(user_id=1, role=RoleEnum.ADMIN)
    assert role_read.user_id == 1
    assert role_read.role == RoleEnum.ADMIN
    
    # Test RoleUpdate schema
    role_update = RoleUpdate(role=RoleEnum.OPERATOR)
    assert role_update.role == RoleEnum.OPERATOR


# Direct test of the RoleEnum values
def test_role_enum_values():
    """Test that RoleEnum has the expected values"""
    assert RoleEnum.ADMIN == "ADMIN"
    assert RoleEnum.OPERATOR == "OPERATOR"
    assert RoleEnum.MEMBER == "MEMBER"
    
    # Test creating from string values
    assert RoleEnum("ADMIN") == RoleEnum.ADMIN
    assert RoleEnum("OPERATOR") == RoleEnum.OPERATOR
    assert RoleEnum("MEMBER") == RoleEnum.MEMBER


@pytest.mark.asyncio
class TestRoleService:
    """Test suite for role service functions"""
    
    @pytest.fixture(scope="function")
    async def admin_user(self, db: AsyncSession):
        """Create an admin user for testing"""
        admin = User(
            email="admin_service@example.com",
            username="admin_service",
            password_hash="hashed_password_for_testing",
            role=RoleEnum.ADMIN
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        yield admin
        # Cleanup
        await db.delete(admin)
        await db.commit()
    
    @pytest.fixture(scope="function")
    async def operator_user(self, db: AsyncSession):
        """Create an operator user for testing"""
        operator = User(
            email="operator_service@example.com",
            username="operator_service",
            password_hash="hashed_password_for_testing",
            role=RoleEnum.OPERATOR
        )
        db.add(operator)
        await db.commit()
        await db.refresh(operator)
        yield operator
        # Cleanup
        await db.delete(operator)
        await db.commit()
    
    @pytest.fixture(scope="function")
    async def member_user(self, db: AsyncSession):
        """Create a member user for testing"""
        member = User(
            email="member_service@example.com",
            username="member_service",
            password_hash="hashed_password_for_testing",
            role=RoleEnum.MEMBER
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        yield member
        # Cleanup
        await db.delete(member)
        await db.commit()
    
    async def test_get_user_role_success(self, db: AsyncSession, member_user):
        """
        Scenario: Successfully retrieve a user's role
        Given a user exists
        When I request their role
        Then I should receive their correct role information
        """
        # Act
        role_result = await get_user_role(db, member_user.id)
        
        # Assert
        assert role_result.user_id == member_user.id
        assert role_result.role == RoleEnum.MEMBER
    
    async def test_get_user_role_nonexistent_user(self, db: AsyncSession):
        """
        Scenario: Attempt to retrieve role for non-existent user
        Given a user ID that doesn't exist
        When I request their role
        Then a NotFoundError should be raised
        """
        # Arrange
        non_existent_id = 99999
        
        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await get_user_role(db, non_existent_id)
        
        assert f"User with ID {non_existent_id} not found" in str(exc_info.value)
    
    async def test_update_user_role_success(self, db: AsyncSession, member_user):
        """
        Scenario: Admin successfully updates a user's role
        Given I am an admin
        When I update a user's role to OPERATOR
        Then the user's role should be updated successfully
        """
        # Arrange
        role_update = RoleUpdate(role=RoleEnum.OPERATOR)
        
        # Act
        updated_role = await update_user_role(
            db, 
            member_user.id, 
            role_update, 
            RoleEnum.ADMIN
        )
        
        # Assert
        assert updated_role.user_id == member_user.id
        assert updated_role.role == RoleEnum.OPERATOR
        
        # Verify in database
        db_role = await get_user_role(db, member_user.id)
        assert db_role.role == RoleEnum.OPERATOR
    
    async def test_update_user_role_non_admin(self, db: AsyncSession, member_user):
        """
        Scenario: Non-admin tries to update a user's role
        Given I am not an admin
        When I try to update a user's role
        Then a PermissionError should be raised
        """
        # Arrange
        role_update = RoleUpdate(role=RoleEnum.OPERATOR)
        
        # Act & Assert - Test with operator role
        with pytest.raises(PermissionError) as exc_info:
            await update_user_role(
                db, 
                member_user.id, 
                role_update, 
                RoleEnum.OPERATOR
            )
        
        assert "Only administrators can change user roles" in str(exc_info.value)
        
        # Act & Assert - Test with member role
        with pytest.raises(PermissionError) as exc_info:
            await update_user_role(
                db, 
                member_user.id, 
                role_update, 
                RoleEnum.MEMBER
            )
        
        assert "Only administrators can change user roles" in str(exc_info.value)
    
    async def test_update_user_role_nonexistent_user(self, db: AsyncSession):
        """
        Scenario: Admin tries to update a non-existent user's role
        Given I am an admin
        When I try to update a non-existent user's role
        Then a NotFoundError should be raised
        """
        # Arrange
        non_existent_id = 99999
        role_update = RoleUpdate(role=RoleEnum.OPERATOR)
        
        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await update_user_role(
                db, 
                non_existent_id, 
                role_update, 
                RoleEnum.ADMIN
            )
        
        assert f"User with ID {non_existent_id} not found" in str(exc_info.value)
    
    async def test_update_user_role_all_roles(self, db: AsyncSession, member_user):
        """
        Scenario: Admin successfully updates a user to all available roles
        Given I am an admin
        When I update a user to each available role
        Then each update should succeed
        """
        # Test updating to each available role
        for role in [RoleEnum.MEMBER, RoleEnum.OPERATOR, RoleEnum.ADMIN]:
            # Arrange
            role_update = RoleUpdate(role=role)
            
            # Act
            updated_role = await update_user_role(
                db, 
                member_user.id, 
                role_update, 
                RoleEnum.ADMIN
            )
            
            # Assert
            assert updated_role.role == role
            
            # Verify in database
            db_role = await get_user_role(db, member_user.id)
            assert db_role.role == role
    
    async def test_update_user_role_self_assignment(self, db: AsyncSession, admin_user):
        """
        Scenario: Admin updates their own role
        Given I am an admin
        When I update my own role to OPERATOR
        Then my role should be updated successfully
        """
        # Arrange
        role_update = RoleUpdate(role=RoleEnum.OPERATOR)
        
        # Act
        updated_role = await update_user_role(
            db, 
            admin_user.id, 
            role_update, 
            RoleEnum.ADMIN
        )
        
        # Assert
        assert updated_role.user_id == admin_user.id
        assert updated_role.role == RoleEnum.OPERATOR
        
        # Verify in database
        db_role = await get_user_role(db, admin_user.id)
        assert db_role.role == RoleEnum.OPERATOR
    
    async def test_update_user_role_idempotent(self, db: AsyncSession, member_user):
        """
        Scenario: Admin updates a user to their current role
        Given I am an admin
        When I update a user's role to their current role
        Then the operation should succeed with no change
        """
        # Arrange
        role_update = RoleUpdate(role=RoleEnum.MEMBER)  # Current role
        
        # Act
        updated_role = await update_user_role(
            db, 
            member_user.id, 
            role_update, 
            RoleEnum.ADMIN
        )
        
        # Assert that it succeeds but no change
        assert updated_role.user_id == member_user.id
        assert updated_role.role == RoleEnum.MEMBER
        
        # Verify in database
        db_role = await get_user_role(db, member_user.id)
        assert db_role.role == RoleEnum.MEMBER

    async def test_update_user_role_edge_case(self, db: AsyncSession, member_user):
        """
        Scenario: Various edge cases in role updating
        Given I am an admin
        When I update a user's role multiple times
        Then all updates should be reflected correctly
        """
        # Test multiple rapid updates
        roles_to_test = [
            RoleEnum.OPERATOR,
            RoleEnum.ADMIN,
            RoleEnum.MEMBER,
            RoleEnum.ADMIN
        ]
        
        for role in roles_to_test:
            # Update to new role
            role_update = RoleUpdate(role=role)
            updated_role = await update_user_role(
                db,
                member_user.id,
                role_update,
                RoleEnum.ADMIN
            )
            
            # Verify update was successful
            assert updated_role.role == role
            
            # Verify in database
            db_role = await get_user_role(db, member_user.id)
            assert db_role.role == role

    async def test_assign_initial_role_default(self, db: AsyncSession, member_user):
        """
        Scenario: Assign default role to a user
        Given a user without a specified role
        When I assign the initial role
        Then the user should be assigned the MEMBER role by default
        """
        # First change the user's role to something else
        # so we can verify the default assignment works
        member_user.role = RoleEnum.OPERATOR
        await db.commit()
        await db.refresh(member_user)
        
        # Now assign the default role (MEMBER)
        role_read = await assign_initial_role(db, member_user.id)
        
        # Verify correct role was assigned
        assert role_read.user_id == member_user.id
        assert role_read.role == RoleEnum.MEMBER
        
        # Verify in database
        stmt = select(User).where(User.id == member_user.id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        assert user.role == RoleEnum.MEMBER
    
    async def test_assign_initial_role_custom(self, db: AsyncSession, member_user):
        """
        Scenario: Assign custom role to a user
        Given a user without a specified role
        When I assign an initial ADMIN role
        Then the user should be assigned the ADMIN role
        """
        # Assign custom role (ADMIN)
        role_read = await assign_initial_role(
            db, 
            member_user.id, 
            role=RoleEnum.ADMIN
        )
        
        # Verify correct role was assigned
        assert role_read.user_id == member_user.id
        assert role_read.role == RoleEnum.ADMIN
        
        # Verify in database
        stmt = select(User).where(User.id == member_user.id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        assert user.role == RoleEnum.ADMIN
    
    async def test_assign_initial_role_nonexistent_user(self, db: AsyncSession):
        """
        Scenario: Attempt to assign role to non-existent user
        Given a user ID that doesn't exist
        When I try to assign an initial role
        Then a NotFoundError should be raised
        """
        # Arrange
        non_existent_id = 99999
        
        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await assign_initial_role(db, non_existent_id)
        
        assert f"User with ID {non_existent_id} not found" in str(exc_info.value)
