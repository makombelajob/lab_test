<?php

namespace App\Entity;

use App\Repository\UserRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Bridge\Doctrine\Validator\Constraints\UniqueEntity;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Security\Core\User\UserInterface;

#[ORM\Entity(repositoryClass: UserRepository::class)]
#[ORM\UniqueConstraint(name: 'UNIQ_IDENTIFIER_EMAIL', fields: ['email'])]
#[UniqueEntity(fields: ['email'], message: 'There is already an account with this email')]
class User implements UserInterface, PasswordAuthenticatedUserInterface
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 180)]
    private ?string $email = null;

    /**
     * @var list<string> The user roles
     */
    #[ORM\Column]
    private array $roles = [];

    /**
     * @var string The hashed password
     */
    #[ORM\Column]
    private ?string $password = null;

    #[ORM\Column(length: 50)]
    private ?string $firstName = null;

    #[ORM\Column(length: 50)]
    private ?string $lastName = null;

    #[ORM\Column(length: 10)]
    private ?string $category = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $createdAt = null;

    #[ORM\Column(nullable: true)]
    private ?\DateTimeImmutable $lastLogin = null;

    #[ORM\Column(length: 36, nullable: true)]
    private ?string $ResetToken = null;

    /**
     * @var Collection<int, Ping>
     */
    #[ORM\OneToMany(targetEntity: Ping::class, mappedBy: 'user')]
    private Collection $ping;

    /**
     * @var Collection<int, Reconn>
     */
    #[ORM\OneToMany(targetEntity: Reconn::class, mappedBy: 'user')]
    private Collection $reconn;

    public function __construct()
    {
        $this->ping = new ArrayCollection();
        $this->reconn = new ArrayCollection();
        $this->createdAt = new \DateTimeImmutable();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getEmail(): ?string
    {
        return $this->email;
    }

    public function setEmail(string $email): static
    {
        $this->email = $email;

        return $this;
    }

    /**
     * A visual identifier that represents this user.
     *
     * @see UserInterface
     */
    public function getUserIdentifier(): string
    {
        return (string) $this->email;
    }

    /**
     * @see UserInterface
     */
    public function getRoles(): array
    {
        $roles = $this->roles;
        // guarantee every user at least has ROLE_USER
        $roles[] = 'ROLE_USER';

        return array_unique($roles);
    }

    /**
     * @param list<string> $roles
     */
    public function setRoles(array $roles): static
    {
        $this->roles = $roles;

        return $this;
    }

    /**
     * @see PasswordAuthenticatedUserInterface
     */
    public function getPassword(): ?string
    {
        return $this->password;
    }

    public function setPassword(string $password): static
    {
        $this->password = $password;

        return $this;
    }

    /**
     * Ensure the session doesn't contain actual password hashes by CRC32C-hashing them, as supported since Symfony 7.3.
     */
    public function __serialize(): array
    {
        $data = (array) $this;
        $data["\0".self::class."\0password"] = hash('crc32c', $this->password);

        return $data;
    }

    #[\Deprecated]
    public function eraseCredentials(): void
    {
        // @deprecated, to be removed when upgrading to Symfony 8
    }

    public function getFirstName(): ?string
    {
        return $this->firstName;
    }

    public function setFirstName(string $firstName): static
    {
        $this->firstName = $firstName;

        return $this;
    }

    public function getLastName(): ?string
    {
        return $this->lastName;
    }

    public function setLastName(string $lastName): static
    {
        $this->lastName = $lastName;

        return $this;
    }

    public function getCategory(): ?string
    {
        return $this->category;
    }

    public function setCategory(string $category): static
    {
        $this->category = $category;

        return $this;
    }

    public function getCreatedAt(): ?\DateTimeImmutable
    {
        return $this->createdAt;
    }

    public function setCreatedAt(\DateTimeImmutable $createdAt): static
    {
        $this->createdAt = $createdAt;

        return $this;
    }

    public function getLastLogin(): ?\DateTimeImmutable
    {
        return $this->lastLogin;
    }

    public function setLastLogin(?\DateTimeImmutable $lastLogin): static
    {
        $this->lastLogin = $lastLogin;

        return $this;
    }

    public function getResetToken(): ?string
    {
        return $this->ResetToken;
    }

    public function setResetToken(?string $ResetToken): static
    {
        $this->ResetToken = $ResetToken;

        return $this;
    }

    /**
     * @return Collection<int, Ping>
     */
    public function getPing(): Collection
    {
        return $this->ping;
    }

    public function addPing(Ping $ping): static
    {
        if (!$this->ping->contains($ping)) {
            $this->ping->add($ping);
            $ping->setUser($this);
        }

        return $this;
    }

    public function removePing(Ping $ping): static
    {
        if ($this->ping->removeElement($ping)) {
            // set the owning side to null (unless already changed)
            if ($ping->getUser() === $this) {
                $ping->setUser(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Reconn>
     */
    public function getReconn(): Collection
    {
        return $this->reconn;
    }

    public function addReconn(Reconn $reconn): static
    {
        if (!$this->reconn->contains($reconn)) {
            $this->reconn->add($reconn);
            $reconn->setUser($this);
        }

        return $this;
    }

    public function removeReconn(Reconn $reconn): static
    {
        if ($this->reconn->removeElement($reconn)) {
            // set the owning side to null (unless already changed)
            if ($reconn->getUser() === $this) {
                $reconn->setUser(null);
            }
        }

        return $this;
    }
}
